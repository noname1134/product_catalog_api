import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ["API_BASE_URL"].rstrip("/")
REQUEST_TIMEOUT_SECONDS = 5

st.title("My Shopping Store")

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

with st.sidebar:
    if st.session_state["access_token"] is None:
        with st.expander("Create an account"):
            with st.form("signup_form"):
                signup_username = st.text_input("Username", key="signup_username")
                signup_password = st.text_input("Password", type="password", key="signup_password")
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email", type="email")
                phone = st.text_input("Phone Number", type="phone")
                country = st.text_input("Country")
                city = st.text_input("City")
                signup_submitted = st.form_submit_button("Create account")
            if signup_submitted:
                user_info = {
                    "username": signup_username,
                    "password": signup_password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone,
                    "country": country,
                    "city": city
                }
                try:
                    response = requests.post(f"{API_BASE_URL}/users/", json=user_info, timeout=REQUEST_TIMEOUT_SECONDS)
                    if response.status_code == 201:
                        st.success("Account created. You can now log in.")
                    elif response.status_code == 409:
                        st.error(response.json()["detail"])
                    elif response.status_code == 422:
                        for error in response.json()["detail"]:
                            field = str(error["loc"][-1])
                            st.error(f"{field}: {error['msg']}")
                    else:
                        st.error("Signup is currently unavailable.")
                except requests.RequestException:
                    st.error("Could not create your account. Please try again.")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Log in")

        if login_submitted:
            try:
                response = requests.post(f"{API_BASE_URL}/users/login", json={"username": username, "password": password}, timeout=REQUEST_TIMEOUT_SECONDS)
                if response.status_code == 200:
                    st.session_state["access_token"] = response.json()["access_token"]
                    st.rerun()
                elif response.status_code == 401:
                    st.error("Invalid username or password.")
                else:
                    st.error("Login is currently unavailable.")
            except requests.RequestException:
                st.error("Login is currently unavailable.")
    else:
        st.success("You are logged in.")
        if st.button("Logout"):
            try:
                response = requests.post(f"{API_BASE_URL}/users/logout", headers={"Authorization": f"Bearer {st.session_state['access_token']}"}, timeout=REQUEST_TIMEOUT_SECONDS)
                if response.status_code == 204:
                    st.session_state["access_token"] = None
                    st.rerun()
                else:
                    st.error("Logout is currently unavailable.")
            except requests.RequestException:
                st.error("Could not log out. Please try again.")


def get_favorites_ids():
    if st.session_state["access_token"] is None:
        return None
    try:
        response = requests.get(f"{API_BASE_URL}/favorites/", headers={"Authorization": f"Bearer {st.session_state['access_token']}"}, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 200:
            return {product["product_id"] for product in response.json()}
        elif response.status_code == 401:
            st.session_state["access_token"] = None
            st.rerun()
        else:
            st.error("Favorites page is currently unavailable.")
    except requests.RequestException:
        st.error("Favorites page is currently unavailable.")



def handle_favorite_click(products: list[dict], favorite_ids: set[int]):
    click = st.session_state["main_favorite_click"]
    token = st.session_state["access_token"]
    if click is None or token is None:
        st.error("Login to add to favorites")
        return
    product_id = products[click["row"]]["product_id"]
    url = f"{API_BASE_URL}/favorites/{product_id}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        if product_id in favorite_ids:
            response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        else:
            response = requests.post(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 204:
            notice = ("success", "Favorites updated.")
        elif response.status_code == 401:
            st.session_state["access_token"] = None
            notice = ("error", "Your session expired. Please log in again.")
        elif response.status_code in (404, 409):
            notice = ("error", response.json()["detail"])
        else:
            notice = ("error", "Could not update favorites. Please try again.")

    except requests.RequestException:
        notice = ("error", "Could not update favorites. Please try again.")

    st.session_state["favorite_notice"] = notice
    notice = st.session_state.pop("favorite_notice", None)
    if notice:
        level, message = notice
        if level == "success":
            st.success(message)
        else:
            st.error(message)


def render_main_page():
    st.write("Browse our available products.")
    with st.form("product_search"):
        search_text = st.text_input(
            "Search products",
            placeholder="For example: sun, table",
        )

        filter_by_price = st.checkbox("Filter by price")
        price_operator = st.selectbox(
            "Price comparison",
            options=["lt", "gt", "eq"],
            format_func=lambda value: {
                "lt": "Less than",
                "gt": "Greater than",
                "eq": "Equal to",
            }[value],
        )

        price = st.number_input(
            "Price (USD)",
            min_value=0.0,
            value=50.0,
            step=1.0,
        )

        filter_by_stock = st.checkbox("Filter by stock")
        stock_operator = st.selectbox(
            "Stock comparison",
            options=["lt", "gt", "eq"],
            format_func=lambda value: {
                "lt": "Less than",
                "gt": "Greater than",
                "eq": "Equal to",
            }[value],
        )

        stock = st.number_input(
            "Quantity",
            min_value=0,
            value=1,
            step=1,
        )

        st.form_submit_button("Search")

    names = [
        term.strip()
        for term in search_text.split(",")
        if term.strip()
    ]

    params = {"name": names}

    if filter_by_price:
        params["price_operator"] = price_operator
        params["price"] = str(price)

    if filter_by_stock:
        params["stock_operator"] = stock_operator
        params["stock"] = str(stock)

    try:
        response = requests.get(f"{API_BASE_URL}/products/", params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        products = response.json()
    except requests.RequestException:
        st.error("Could not load products. Please try again shortly.")
        st.stop()

    if not products:
        st.info("No products found.")
    else:
        table_rows = []
        favorite_ids = get_favorites_ids()
        can_manage_favorites = (st.session_state["access_token"] is not None and favorite_ids is not None)
        if can_manage_favorites:
            for product in products:
                table_rows.append({
                    "Product": product["name"],
                    "Price (USD)": product["price"],
                    "In stock": product["stock_quantity"],
                    "Favorite": ("Remove favorite" if favorite_ids and product["product_id"] in favorite_ids else "Add favorite")
                })
            st.dataframe(
                table_rows, column_config={
                    "Favorite": st.column_config.ButtonColumn("Favorite", key="main_favorite_click", on_click=handle_favorite_click, args=(products, favorite_ids))},
                hide_index=True, width="stretch")
        else:
            for product in products:
                table_rows.append({
                    "Product": product["name"],
                    "Price (USD)": product["price"],
                    "In stock": product["stock_quantity"]
                })
            st.dataframe(table_rows, hide_index=True, width="stretch")


def render_favorites_page():
    st.write("Your favorite products list")
    if st.session_state["access_token"] is None:
        st.error("Please log in to access favorites.")
        st.stop()
    try:
        response = requests.get(f"{API_BASE_URL}/favorites/", headers={"Authorization": f"Bearer {st.session_state['access_token']}"}, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 200:
            favorites = response.json()
            if not favorites:
                st.info("Favorite list is empty.")
            else:
                favorite_ids = {product["product_id"] for product in favorites}
                table_rows = []
                for product in favorites:
                    table_rows.append({
                        "Product": product["name"],
                        "Price (USD)": product["price"],
                        "In stock": product["stock_quantity"],
                        "Favorite": "Remove favorite"
                    })

                st.dataframe(table_rows, column_config={
                    "Favorite": st.column_config.ButtonColumn("Favorite", key="main_favorite_click", on_click=handle_favorite_click, args=(favorites, favorite_ids))},
                             hide_index=True, width="stretch")
        elif response.status_code == 401:
            st.session_state["access_token"] = None
            st.rerun()
        else:
            st.error("Favorites page is currently unavailable.")
    except requests.RequestException:
        st.error("Favorites page is currently unavailable.")


selected_page = st.sidebar.radio("Navigation", ["Main", "Orders", "Favorites", "Chat assistant"])
if selected_page == "Main":
    render_main_page()
elif selected_page == "Favorites":
    render_favorites_page()
else:
    if st.session_state["access_token"] is None:
        st.info("Please log in to access this page.")
        st.stop()
