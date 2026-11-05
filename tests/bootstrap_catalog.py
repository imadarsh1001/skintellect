"""Create a tiny synthetic catalog for checks; refuse to overwrite existing data."""

import sqlite3

from skintellect.catalog.personas import init_personas_db
from skintellect.config import DB_PATH
from skintellect.database import init_db, migrate, run_migrations


def main():
    # The check runner creates an empty file and passes its absolute path explicitly.
    from pathlib import Path

    if Path(DB_PATH).stat().st_size:
        raise RuntimeError("Test catalog must be an empty file")
    init_db(DB_PATH)
    run_migrations()
    init_personas_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO products(id,brand,name,domain,category,ingredients_json) "
            "VALUES(1,'Fixture','Synthetic moisturizer','skin','Moisturizers',?)",
            ('[{"name":"Water"},{"name":"Glycerin"}]',),
        )
        connection.execute(
            "INSERT INTO ingredients(id,name,slug,function) VALUES(1,'Water','water','Solvent')"
        )
        connection.execute("INSERT INTO product_ingredients(product_id,ingredient_id) VALUES(1,1)")
    migrate(DB_PATH)


if __name__ == "__main__":
    main()
