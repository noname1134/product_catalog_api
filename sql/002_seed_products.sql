-- Sample catalog for development. Run once after creating the products table.
-- No product IDs are supplied; MySQL generates them.
START TRANSACTION;

INSERT INTO products (name, description, price, stock_quantity)
VALUES
    ('Classic Sunglasses', 'Black sunglasses with UV400 lenses and a lightweight plastic frame.', 24.99, 25),
    ('Sport Sunglasses', 'Wraparound sunglasses with UV400 lenses and rubber nose pads.', 59.99, 8),
    ('Sun Hat', 'Beige cotton hat with a wide brim and an adjustable chin strap.', 19.99, 0),
    ('Portable Table', 'Foldable camping table measuring 60 x 40 x 26 cm.', 39.99, 15),
    ('Dining Table', 'Rectangular wooden dining table measuring 120 x 80 x 75 cm, seating four people.', 249.99, 4),
    ('Basketball', 'Size 7 basketball, approximately 75 cm in circumference, with a rubber outdoor surface.', 25.00, 20),
    ('Football', 'Size 5 football with a synthetic cover for recreational outdoor play.', 22.50, 10),
    ('Water Bottle', 'Reusable 750 ml stainless steel bottle with a screw-top lid.', 15.00, 30),
    ('Wireless Mouse', 'Battery-powered wireless mouse with a USB receiver and three buttons. Requires one AA battery.', 29.99, 0),
    ('Backpack', '20 litre polyester backpack with two shoulder straps and a front zip pocket.', 49.99, 12);

COMMIT;
