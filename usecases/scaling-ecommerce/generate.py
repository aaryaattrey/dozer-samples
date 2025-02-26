import dbldatagen as dg

import pyspark
from delta import *


def generate(data_size, output_folder):

    builder = pyspark.sql.SparkSession.builder.appName("MyApp") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.warehouse.dir", output_folder)

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    # Create the tables using Delta format if they don't exist
    spark.sql("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT,
            name STRING,
            email STRING,
            address STRING,
            created_at TIMESTAMP
        )
        USING Delta
    """)

    spark.sql("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT,
            customer_id INT,
            order_date TIMESTAMP,
            total_amount DOUBLE
        )
        USING Delta
    """)

    spark.sql("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INT,
            order_id INT,
            product_id INT,
            quantity INT,
            price DOUBLE
    
        )
        USING Delta
    """)

    spark.sql("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT,
            name STRING,
            category STRING,
            price DOUBLE,
            created_at TIMESTAMP,
    
            special STRING,
            brand STRING,
            description STRING,
            warranty STRING,
            quantity STRING,
            weight STRING,
            color STRING,
            size STRING,
            material STRING,
            country STRING,
            upc STRING,
            variants STRING,
            supplier STRING,
            availability STRING,
            rating STRING,
            release_date STRING
        )
        USING Delta
    """)

    # Get the table schemas
    customers_schema = spark.table("customers").schema
    orders_schema = spark.table("orders").schema
    order_items_schema = spark.table("order_items").schema
    products_schema = spark.table("products").schema


    # Define column specifications for data generation
    customers_dataspec = (
        dg.DataGenerator(spark, rows=data_size['CUSTOMER_COUNT'], partitions=8)
        .withSchema(customers_schema)
        .withColumnSpec("customer_id", minValue=data_size['CUSTOMER_MIN'], maxValue=data_size['CUSTOMER_IDS'], step=1)
        .withColumnSpec("name", template=r"\w{5,10} \w{5,10}")
        .withColumnSpec("email", template=r"\w{5,10}@\w{5,10}.com")
        .withColumnSpec("address", template=r"\w{5,10} Street, City")
        .withColumnSpec("created_at", minValue="2022-01-01", maxValue="2022-12-31")
    )

    orders_dataspec = (
        dg.DataGenerator(spark, rows=data_size['ORDER_COUNT'], partitions=8)
        .withSchema(orders_schema)
        .withColumnSpec("order_id", minValue=data_size['ORDER_MIN'], maxValue=data_size['ORDER_IDS'], step=1)
        .withColumnSpec("customer_id", minValue=data_size['CUSTOMER_MIN'], maxValue=data_size['CUSTOMER_IDS'], step=1)
        .withColumnSpec("order_date", minValue="2022-01-01", maxValue="2022-12-31")
        .withColumnSpec("total_amount", minValue=10, maxValue=1000)
    )

    order_items_dataspec = (
        dg.DataGenerator(spark, rows=data_size['ORDER_ITEMS_COUNT'], partitions=8)
        .withSchema(order_items_schema)
        .withColumnSpec("order_item_id", minValue=data_size['ORDER_ITEMS_MIN'], maxValue=data_size['ORDER_ITEMS_IDS'], step=1)
        .withColumnSpec("order_id", minValue=data_size['ORDER_MIN'], maxValue=data_size['ORDER_IDS'], step=1)
        .withColumnSpec("product_id", minValue=data_size['PRODUCT_MIN'], maxValue=data_size['PRODUCT_IDS'], step=1)
        .withColumnSpec("quantity", minValue=1, maxValue=10)
        .withColumnSpec("price", minValue=10.0, maxValue=100.0)
    )

    products_dataspec = (
        dg.DataGenerator(spark, rows=data_size['PRODUCT_COUNT'], partitions=8)
        .withSchema(products_schema)
        .withColumnSpec("product_id", minValue=data_size['PRODUCT_MIN'], maxValue=data_size['PRODUCT_IDS'], step=1)
        .withColumnSpec("name", template=r"Product \w{5,10}")
        .withColumnSpec("category", template=r"\w{5,10}")
        .withColumnSpec("price", minValue=10.0, maxValue=100.0)
        .withColumnSpec("created_at", minValue="2022-01-01", maxValue="2022-12-31")
        .withColumnSpec("special", template=r"\w{32}")
        .withColumnSpec("brand", template=r"\w{32}")
        .withColumnSpec("description", template=r"\w{32}")
        .withColumnSpec("warranty", template=r"\w{32}")
        .withColumnSpec("quantity", template=r"\w{32}")
        .withColumnSpec("weight", template=r"\w{32}")
        .withColumnSpec("color", template=r"\w{32}")
        .withColumnSpec("size", template=r"\w{32}")
        .withColumnSpec("material", template=r"\w{32}")
        .withColumnSpec("country", template=r"\w{32}")
        .withColumnSpec("upc", template=r"\w{32}")
        .withColumnSpec("variants", template=r"\w{32}")
        .withColumnSpec("supplier", template=r"\w{32}")
        .withColumnSpec("availability", template=r"\w{32}")
        .withColumnSpec("rating", template=r"\w{32}")
        .withColumnSpec("release_date", template=r"\w{32}")
    )

    # Generate the data
    customers_data = customers_dataspec.build()
    orders_data = orders_dataspec.build()
    order_items_data = order_items_dataspec.build()
    products_data = products_dataspec.build()

    # Save the generated data as Delta tables
    customers_data.write.format("delta").mode("overwrite").saveAsTable("customers")
    orders_data.write.format("delta").mode("overwrite").saveAsTable("orders")
    order_items_data.write.format("delta").mode("overwrite").saveAsTable("order_items")
    products_data.write.format("delta").mode("overwrite").saveAsTable("products")


if __name__ == '__main__':

#    data_size = {
#        'CUSTOMER_MIN': 1,
#        'CUSTOMER_IDS': 400_000,
#        'CUSTOMER_COUNT': 400_000,
#        'ORDER_MIN': 1,
#        'ORDER_IDS': 200_000,
#        'ORDER_COUNT': 200_000,
#        'PRODUCT_MIN': 1,
#        'PRODUCT_IDS': 100_000,
#        'PRODUCT_COUNT': 100_000,
#        'ORDER_ITEMS_MIN': 1,
#        'ORDER_ITEMS_IDS': 10_000_000,
#        'ORDER_ITEMS_COUNT': 10_000_000
#    }

#    generate(data_size, output_folder='./1d-data')

    data_size = {
        'CUSTOMER_MIN': 1,
        'CUSTOMER_IDS': 2_000_000,
        'CUSTOMER_COUNT': 2_000_000,
        'ORDER_MIN': 1,
        'ORDER_IDS': 10_000_000,
        'ORDER_COUNT': 10_000_000,
        'PRODUCT_MIN': 1,
        'PRODUCT_IDS': 5_000_000,
        'PRODUCT_COUNT': 5_000_000,
        'ORDER_ITEMS_MIN': 1,
        'ORDER_ITEMS_IDS': 50_000_000,
        'ORDER_ITEMS_COUNT': 50_000_000
    }

    generate(data_size, output_folder='./2-active-data')

#    data_size = {
#        'CUSTOMER_MIN': 1,
#        'CUSTOMER_IDS': 11_000_000,
#        'CUSTOMER_COUNT': 11_000_000,
#        'ORDER_MIN': 1,
#        'ORDER_IDS': 11_000_000,
#        'ORDER_COUNT': 11_000_000,
#        'PRODUCT_MIN': 1,
#        'PRODUCT_IDS': 16_000_000,
#        'PRODUCT_COUNT': 16_000_000,
#        'ORDER_ITEMS_MIN': 1,
#        'ORDER_ITEMS_IDS': 100_000_000,
#        'ORDER_ITEMS_COUNT': 100_000_000
#    }

#    generate(data_size, output_folder='./3h-data')
