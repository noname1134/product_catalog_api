"""Streamlit front end for My Shopping Store."""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ["API_BASE_URL"].rstrip("/")
REQUEST_TIMEOUT_SECONDS = 5
CHAT_REPLY_TIMEOUT_SECONDS = 60  # the assistant can take a while to answer

PAGES = ["Main", "Orders", "Favorites", "Chat assistant"]
COMPARISON_LABELS = {"lt": "Less than", "gt": "Greater than", "eq": "Equal to"}
DEFAULT_QUANTITY = 1

# Widget keys (also used to read click / edit state inside callbacks).
PRODUCT_TABLE_KEY = "product_table"
ADD_TO_ORDER_KEY = "add_to_order"
FAVORITE_KEY = "main_favorite_click"
REMOVE_ITEM_KEY = "remove_cart_item"
ORDERS_NOTICE_KEY = "orders_notice"
ACCOUNT_NOTICE_KEY = "account_notice"
CHAT_SESSION_KEY = "chat_session_id"

FAVORITES_UNAVAILABLE = "Favorites page is currently unavailable."
SESSION_EXPIRED = "Your session expired. Please log in again."
CART_UNAVAILABLE = "Your cart is currently unavailable."
HISTORY_UNAVAILABLE = "Order history is currently unavailable."
CHAT_UNAVAILABLE = "The chat assistant is currently unavailable."


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def api_url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def get_token() -> str | None:
    return st.session_state["access_token"]


def clear_session() -> None:
    st.session_state["access_token"] = None
    st.session_state.pop(CHAT_SESSION_KEY, None)  # a chat session belongs to one user


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_token()}"}


def require_login() -> None:
    if get_token() is None:
        st.info("Please log in to access this page.")
        st.stop()


def show_notice(level: str, message: str) -> None:
    if level == "success":
        st.success(message)
    else:
        st.error(message)


def error_detail(response: requests.Response, fallback: str) -> str:
    """Pull a readable message out of an API error response."""
    try:
        detail = response.json()["detail"]
    except (ValueError, KeyError, TypeError):
        return fallback
    if isinstance(detail, list):
        return "; ".join(f"{error['loc'][-1]}: {error['msg']}" for error in detail)
    return str(detail)


# --------------------------------------------------------------------------
# Sidebar: account
# --------------------------------------------------------------------------

def sign_up(user_info: dict) -> None:
    try:
        response = requests.post(
            api_url("/users/"), json=user_info, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.RequestException:
        st.error("Could not create your account. Please try again.")
        return

    if response.status_code == 201:
        st.success("Account created. You can now log in.")
    elif response.status_code == 409:
        st.error(error_detail(response, "This account already exists."))
    elif response.status_code == 422:
        for error in response.json()["detail"]:
            st.error(f"{error['loc'][-1]}: {error['msg']}")
    else:
        st.error("Signup is currently unavailable.")


def render_signup_form() -> None:
    with st.expander("Create an account"):
        with st.form("signup_form"):
            username = st.text_input("Username", key="signup_username")
            password = st.text_input("Password", type="password", key="signup_password")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            country = st.text_input("Country")
            city = st.text_input("City")
            submitted = st.form_submit_button("Create account")

        if submitted:
            sign_up({
                "username": username,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "country": country,
                "city": city,
            })


def log_in(username: str, password: str) -> None:
    try:
        response = requests.post(
            api_url("/users/login"),
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error("Login is currently unavailable.")
        return

    if response.status_code == 200:
        st.session_state["access_token"] = response.json()["access_token"]
        st.rerun()
    elif response.status_code == 401:
        st.error("Invalid username or password.")
    else:
        st.error("Login is currently unavailable.")


def render_login_form() -> None:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        log_in(username, password)


def log_out() -> None:
    try:
        response = requests.post(
            api_url("/users/logout"),
            headers=auth_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error("Could not log out. Please try again.")
        return

    if response.status_code == 204:
        clear_session()
        st.rerun()
    else:
        st.error("Logout is currently unavailable.")


def delete_account() -> None:
    try:
        response = requests.delete(
            api_url("/users/me"),
            headers=auth_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error("Could not delete your account. Please try again.")
        return

    if response.status_code in (200, 204):
        clear_session()
        st.session_state[ACCOUNT_NOTICE_KEY] = ("success", "Your account was deleted.")
        st.rerun()
    elif response.status_code == 401:
        clear_session()
        st.session_state[ACCOUNT_NOTICE_KEY] = ("error", SESSION_EXPIRED)
        st.rerun()
    else:
        st.error(error_detail(response, "Could not delete your account. Please try again."))


@st.dialog("Delete your account?")
def confirm_delete_account() -> None:
    st.write("This permanently deletes your account. This can't be undone.")
    confirm_column, cancel_column = st.columns(2)
    if confirm_column.button("Yes, delete", type="primary"):
        delete_account()
    if cancel_column.button("Cancel"):
        st.rerun()


def render_account_sidebar() -> None:
    with st.sidebar:
        if get_token() is None:
            notice = st.session_state.pop(ACCOUNT_NOTICE_KEY, None)
            if notice:
                show_notice(*notice)
            render_signup_form()
            render_login_form()
        else:
            st.success("You are logged in.")
            if st.button("Logout"):
                log_out()
            if st.button("Delete account"):
                confirm_delete_account()


# --------------------------------------------------------------------------
# Favorites
# --------------------------------------------------------------------------

def fetch_favorites() -> list[dict] | None:
    """Return the user's favorite products, or None if they could not be loaded."""
    try:
        response = requests.get(
            api_url("/favorites/"),
            headers=auth_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error(FAVORITES_UNAVAILABLE)
        return None

    if response.status_code == 200:
        return response.json()
    if response.status_code == 401:
        clear_session()
        st.rerun()
    st.error(FAVORITES_UNAVAILABLE)
    return None


def get_favorite_ids() -> set[int] | None:
    if get_token() is None:
        return None
    favorites = fetch_favorites()
    if favorites is None:
        return None
    return {product["product_id"] for product in favorites}


def handle_favorite_click(products: list[dict], favorite_ids: set[int] | None) -> None:
    click = st.session_state.get(FAVORITE_KEY)
    if click is None or get_token() is None:
        st.error("Login to add to favorites")
        return

    product_id = products[click["row"]]["product_id"]
    url = api_url(f"/favorites/{product_id}")
    is_favorite = product_id in (favorite_ids or set())

    try:
        send = requests.delete if is_favorite else requests.post
        response = send(url, headers=auth_headers(), timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException:
        show_notice("error", "Could not update favorites. Please try again.")
        return

    if response.status_code == 204:
        show_notice("success", "Favorites updated.")
    elif response.status_code == 401:
        clear_session()
        show_notice("error", SESSION_EXPIRED)
    elif response.status_code in (404, 409):
        show_notice("error", error_detail(response, "Could not update favorites."))
    else:
        show_notice("error", "Could not update favorites. Please try again.")


# --------------------------------------------------------------------------
# Orders
# --------------------------------------------------------------------------

def handle_add_to_order_click(products: list[dict]) -> None:
    click = st.session_state.get(ADD_TO_ORDER_KEY)
    if click is None or get_token() is None:
        st.error("Login to add to your order")
        return

    row = click["row"]
    product = products[row]

    edited_rows = st.session_state.get(PRODUCT_TABLE_KEY, {}).get("edited_rows", {})
    quantity = int(edited_rows.get(row, {}).get("Quantity") or DEFAULT_QUANTITY)

    try:
        response = requests.post(
            api_url("/orders/temp/items"),
            json={"product_id": product["product_id"], "quantity": quantity},
            headers=auth_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        show_notice("error", "Could not add the item to your order. Please try again.")
        return

    if response.status_code in (200, 201):
        show_notice("success", f"Added {quantity} x {product['name']} to your order.")
    elif response.status_code == 401:
        clear_session()
        show_notice("error", SESSION_EXPIRED)
    elif response.status_code in (404, 409, 422):
        show_notice("error", error_detail(response, "Could not add the item to your order."))
    else:
        show_notice("error", "Could not add the item to your order. Please try again.")


# --------------------------------------------------------------------------
# Orders page
# --------------------------------------------------------------------------

def flash(level: str, message: str) -> None:
    """Store a notice that is shown at the top of the Orders page on the next run."""
    st.session_state[ORDERS_NOTICE_KEY] = (level, message)


def show_flash() -> None:
    notice = st.session_state.pop(ORDERS_NOTICE_KEY, None)
    if notice:
        show_notice(*notice)


def order_id_of(order: dict) -> int | None:
    return order.get("order_id", order.get("id"))


def item_row(item: dict) -> dict:
    return {
        "Product": item.get("name", item.get("product_name", "")),
        "Price (USD)": item.get("price"),
        "Quantity": item.get("quantity"),
    }


def order_total(order: dict) -> float:
    if order.get("total_price") is not None:
        return float(order["total_price"])
    return sum(
        float(item.get("price", 0)) * item.get("quantity", 0)
        for item in order.get("items", [])
    )


def get_orders_resource(path: str, failure: str) -> requests.Response | None:
    """GET an orders endpoint. Returns None (after showing an error) if unreachable."""
    try:
        response = requests.get(
            api_url(path), headers=auth_headers(), timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.RequestException:
        st.error(failure)
        return None

    if response.status_code == 401:
        clear_session()
        st.rerun()
    return response


def fetch_cart() -> dict | None:
    """Return the current temp order, or None when there is no cart yet."""
    response = get_orders_resource("/orders/temp", CART_UNAVAILABLE)
    if response is None:
        st.stop()
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        st.error(CART_UNAVAILABLE)
        st.stop()
    return response.json()


def fetch_closed_orders() -> list[dict]:
    """Return the user's purchased orders (the API also lists the open TEMP cart)."""
    response = get_orders_resource("/orders/", HISTORY_UNAVAILABLE)
    if response is None:
        return []
    if response.status_code != 200:
        st.error(HISTORY_UNAVAILABLE)
        return []
    return [
        order for order in response.json()
        if str(order.get("status", "")).upper() == "CLOSE"
    ]


def run_order_action(
    method: str, path: str, *, success: str, failure: str, json: dict | None = None
) -> bool:
    """Call an orders endpoint with the user's token and flash the outcome."""
    try:
        response = requests.request(
            method,
            api_url(path),
            json=json,
            headers=auth_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        flash("error", failure)
        return False

    if response.status_code in (200, 201, 204):
        flash("success", success)
        return True
    if response.status_code == 401:
        clear_session()
        flash("error", SESSION_EXPIRED)
    elif response.status_code in (400, 404, 409, 422):
        flash("error", error_detail(response, failure))
    else:
        flash("error", failure)
    return False


def handle_remove_item_click(items: list[dict]) -> None:
    click = st.session_state.get(REMOVE_ITEM_KEY)
    if click is None or get_token() is None:
        return

    item = items[click["row"]]
    name = item_row(item)["Product"]
    run_order_action(
        "DELETE",
        f"/orders/temp/{item['product_id']}",
        success=f"Removed {name} from your cart.",
        failure="Could not remove the item. Please try again.",
    )


def handle_clear_cart_click() -> None:
    run_order_action(
        "DELETE",
        "/orders/temp",
        success="Your cart was cleared.",
        failure="Could not clear your cart. Please try again.",
    )


def render_checkout_form(cart_id: int) -> None:
    with st.form("checkout_form"):
        shipping_address = st.text_input("Shipping address")
        submitted = st.form_submit_button("Purchase order")

    if not submitted:
        return
    if not shipping_address.strip():
        st.error("Please enter a shipping address.")
        return

    run_order_action(
        "POST",
        f"/orders/{cart_id}/checkout",
        json={"shipping_address": shipping_address.strip()},
        success="Order purchased. Thank you!",
        failure="Could not complete your purchase. Please try again.",
    )
    st.rerun()


def render_cart_section(cart: dict | None) -> None:
    st.subheader("Your cart")
    items = cart.get("items", []) if cart else []
    if not items:
        st.info("Your cart is empty.")
        return

    st.dataframe(
        [{**item_row(item), "Remove": "Remove"} for item in items],
        hide_index=True,
        width="stretch",
        column_config={
            "Remove": st.column_config.ButtonColumn(
                "Remove",
                key=REMOVE_ITEM_KEY,
                on_click=handle_remove_item_click,
                args=(items,),
            ),
        },
    )
    st.write(f"**Total: ${order_total(cart):,.2f}**")
    render_checkout_form(order_id_of(cart))
    st.button("Clear cart", on_click=handle_clear_cart_click)


def render_order_history() -> None:
    st.subheader("Order history")
    orders = fetch_closed_orders()
    if not orders:
        st.info("No purchased orders yet.")
        return

    newest_first = sorted(orders, key=lambda o: order_id_of(o) or 0, reverse=True)
    st.dataframe(
        [
            {
                "Order": f"#{order_id_of(order)}",
                "Date": str(order.get("creation_date", "")).replace("T", " ")[:16],
                "Total (USD)": order_total(order),
                "Shipping address": order.get("shipping_address"),
            }
            for order in newest_first
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "Total (USD)": st.column_config.NumberColumn("Total (USD)", format="%.2f"),
        },
    )


def render_orders_page() -> None:
    show_flash()
    require_login()

    cart = fetch_cart()
    render_cart_section(cart)
    render_order_history()


# --------------------------------------------------------------------------
# Main page
# --------------------------------------------------------------------------

def comparison_selectbox(label: str) -> str:
    return st.selectbox(
        label,
        options=list(COMPARISON_LABELS),
        format_func=COMPARISON_LABELS.get,
    )


def render_search_form() -> dict:
    """Render the search form and return the matching query parameters."""
    with st.form("product_search"):
        search_text = st.text_input(
            "Search products",
            placeholder="For example: sun, table",
        )

        filter_by_price = st.checkbox("Filter by price")
        price_operator = comparison_selectbox("Price comparison")
        price = st.number_input("Price (USD)", min_value=0.0, value=50.0, step=1.0)

        filter_by_stock = st.checkbox("Filter by stock")
        stock_operator = comparison_selectbox("Stock comparison")
        stock = st.number_input("Quantity", min_value=0, value=1, step=1)

        st.form_submit_button("Search")

    params = {
        "name": [term.strip() for term in search_text.split(",") if term.strip()]
    }
    if filter_by_price:
        params["price_operator"] = price_operator
        params["price"] = str(price)
    if filter_by_stock:
        params["stock_operator"] = stock_operator
        params["stock"] = str(stock)
    return params


def fetch_products(params: dict) -> list[dict]:
    try:
        response = requests.get(
            api_url("/products/"), params=params, timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        st.error("Could not load products. Please try again shortly.")
        st.stop()


def product_row(product: dict) -> dict:
    return {
        "Product": product["name"],
        "Price (USD)": product["price"],
        "In stock": product["stock_quantity"],
    }


def render_member_products_table(products: list[dict]) -> None:
    favorite_ids = get_favorite_ids() or set()

    rows = [
        {
            **product_row(product),
            "Quantity": DEFAULT_QUANTITY,
            "Add to order": "Add to order",
            "Favorite": (
                "Remove favorite" if product["product_id"] in favorite_ids else "Add favorite"
            ),
        }
        for product in products
    ]

    st.data_editor(
        rows,
        key=PRODUCT_TABLE_KEY,
        hide_index=True,
        width="stretch",
        disabled=["Product", "Price (USD)", "In stock"],
        column_config={
            "Quantity": st.column_config.NumberColumn(
                "Amount", min_value=1, max_value=99, step=1, required=True, format="%d"
            ),
            "Add to order": st.column_config.ButtonColumn(
                "Add to order",
                key=ADD_TO_ORDER_KEY,
                on_click=handle_add_to_order_click,
                args=(products,),
            ),
            "Favorite": st.column_config.ButtonColumn(
                "Favorite",
                key=FAVORITE_KEY,
                on_click=handle_favorite_click,
                args=(products, favorite_ids),
            ),
        },
    )


def render_main_page() -> None:
    st.write("Browse our available products.")
    products = fetch_products(render_search_form())

    if not products:
        st.info("No products found.")
    elif get_token() is not None:
        render_member_products_table(products)
    else:
        st.dataframe(
            [product_row(product) for product in products],
            hide_index=True,
            width="stretch",
        )


# --------------------------------------------------------------------------
# Favorites page
# --------------------------------------------------------------------------

def render_favorites_page() -> None:
    st.write("Your favorite products list")
    if get_token() is None:
        st.error("Please log in to access favorites.")
        st.stop()

    favorites = fetch_favorites()
    if favorites is None:
        return
    if not favorites:
        st.info("Favorite list is empty.")
        return

    favorite_ids = {product["product_id"] for product in favorites}
    rows = [{**product_row(product), "Favorite": "Remove favorite"} for product in favorites]

    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
        column_config={
            "Favorite": st.column_config.ButtonColumn(
                "Favorite",
                key=FAVORITE_KEY,
                on_click=handle_favorite_click,
                args=(favorites, favorite_ids),
            ),
        },
    )


# --------------------------------------------------------------------------
# Chat assistant page
# --------------------------------------------------------------------------

def message_role(message: dict) -> str:
    return "user" if str(message.get("role", "")).lower() == "user" else "assistant"


def message_text(message: dict) -> str:
    return message.get("content", message.get("message", ""))


def reply_text(reply: dict) -> str:
    return reply.get("reply", reply.get("message", reply.get("content", "")))


def forget_chat_session() -> None:
    st.session_state.pop(CHAT_SESSION_KEY, None)


def create_chat_session() -> str | None:
    try:
        response = requests.post(
            api_url("/chat/sessions"),
            headers=auth_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error(CHAT_UNAVAILABLE)
        return None

    if response.status_code == 201:
        session_id = response.json()["session_id"]
        st.session_state[CHAT_SESSION_KEY] = session_id
        return session_id
    if response.status_code == 401:
        clear_session()
        st.rerun()
    st.error(CHAT_UNAVAILABLE)
    return None


def fetch_chat_messages(session_id: str) -> list[dict]:
    try:
        response = requests.get(
            api_url(f"/chat/sessions/{session_id}/messages"),
            headers=auth_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error(CHAT_UNAVAILABLE)
        return []

    if response.status_code == 200:
        return response.json()
    if response.status_code == 401:
        clear_session()
        st.rerun()
    if response.status_code == 404:
        forget_chat_session()  # the next message starts a fresh session
        return []
    st.error(CHAT_UNAVAILABLE)
    return []


def send_chat_message(session_id: str, prompt: str) -> str | None:
    """Return the assistant's reply, or None after showing an error."""
    try:
        response = requests.post(
            api_url(f"/chat/sessions/{session_id}/messages"),
            json={"message": prompt},
            headers=auth_headers(),
            timeout=CHAT_REPLY_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error(CHAT_UNAVAILABLE)
        return None

    if response.status_code == 200:
        return reply_text(response.json())
    if response.status_code == 401:
        clear_session()
        st.rerun()
    if response.status_code == 404:
        forget_chat_session()
    if response.status_code in (404, 409, 429, 503):
        st.error(error_detail(response, CHAT_UNAVAILABLE))
    else:
        st.error(CHAT_UNAVAILABLE)
    return None


def render_chat_page() -> None:
    require_login()
    st.write("Chat with our shopping assistant.")

    session_id = st.session_state.get(CHAT_SESSION_KEY)
    if session_id:
        st.button("New chat", on_click=forget_chat_session)
        for message in fetch_chat_messages(session_id):
            with st.chat_message(message_role(message)):
                st.write(message_text(message))

    prompt = st.chat_input("Ask the assistant")
    if not prompt:
        return

    session_id = st.session_state.get(CHAT_SESSION_KEY) or create_chat_session()
    if session_id is None:
        return

    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = send_chat_message(session_id, prompt)
        if reply is not None:
            st.write(reply)


# --------------------------------------------------------------------------
# App entry point
# --------------------------------------------------------------------------

def main() -> None:
    st.title("My Shopping Store")

    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None

    render_account_sidebar()
    selected_page = st.sidebar.radio("Navigation", PAGES)

    if selected_page == "Main":
        render_main_page()
    elif selected_page == "Orders":
        render_orders_page()
    elif selected_page == "Favorites":
        render_favorites_page()
    elif selected_page == "Chat assistant":
        render_chat_page()


main()