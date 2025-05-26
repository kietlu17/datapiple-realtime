from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, FloatType
from pyspark.sql.functions import  col
from pyspark.sql import SparkSession
import psycopg2

# Initialize Spark session
spark = SparkSession.builder \
        .appName('SparkKafkaToPostgres') \
        .config('spark.jars.packages', "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3," 
                                        "org.postgresql:postgresql:42.5.0") \
        .getOrCreate()

# Read data from Kafka topic
df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "book") \
        .option("startingOffsets", "earliest") \
        .load()

# Chuyển đổi `value` từ binary sang JSON
json_df = df.selectExpr("CAST(value AS STRING) as json_value")

# Giải nén JSON để lấy các cột cụ thể
cleaned_df = json_df.select(
    F.get_json_object("json_value", "$.bookUrl").alias("bookUrl"),
    F.get_json_object("json_value", "$.authorUrl").alias("authorUrl"),
    F.get_json_object("json_value", "$.prices").alias("prices"),
    F.get_json_object("json_value", "$.rating").alias("rating"),
    F.get_json_object("json_value", "$.ratingcount").alias("ratingcount"),
    F.get_json_object("json_value", "$.reviews").alias("reviews"),
    F.get_json_object("json_value", "$.fivestars").alias("fivestars"),
    F.get_json_object("json_value", "$.fourstars").alias("fourstars"),
    F.get_json_object("json_value", "$.threestars").alias("threestars"),
    F.get_json_object("json_value", "$.twostars").alias("twostars"),
    F.get_json_object("json_value", "$.onestar").alias("onestar"),
    F.get_json_object("json_value", "$.pages").alias("pages"),
    F.get_json_object("json_value", "$.publish").alias("publish"),
    F.get_json_object("json_value", "$.author").alias("author"),
    F.get_json_object("json_value", "$.bookname").alias("bookname"),
    F.get_json_object("json_value", "$.describe").alias("describe"),
    F.get_json_object("json_value", "$.cover").alias("cover"),
    F.get_json_object("json_value", "$.genre").alias("genre")
)

# Data cleaning
cleaned_df = cleaned_df.withColumn("book_id", F.regexp_extract("bookUrl", r'book/show/(\d+)', 1).cast(IntegerType())) \
    .withColumn("author_id", F.regexp_extract("authorUrl", r'author/show/(\d+)', 1).cast(IntegerType())) \
    .withColumn("prices", F.regexp_extract("prices", r'\$(\d+\.\d+)', 1).cast(FloatType())) \
    .withColumn("rating", col("rating").cast(FloatType())) \
    .withColumn("ratingcount", F.regexp_replace("ratingcount", ',', '').cast(IntegerType())) \
    .withColumn("reviews", F.regexp_replace("reviews", ',', '').cast(IntegerType())) \
    .withColumn("fivestars", F.regexp_replace(col("fivestars"), r"[^\d]", "").cast(IntegerType())) \
    .withColumn("fourstars", F.regexp_replace(col("fourstars"), r"[^\d]", "").cast(IntegerType())) \
    .withColumn("threestars", F.regexp_replace(col("threestars"), r"[^\d]", "").cast(IntegerType())) \
    .withColumn("twostars", F.regexp_replace(col("twostars"), r"[^\d]", "").cast(IntegerType())) \
    .withColumn("onestar", F.regexp_replace(col("onestar"), r"[^\d]", "").cast(IntegerType())) \
    .withColumn("pages_n", F.regexp_extract("pages", r'(\d+)', 1).cast(IntegerType())) \
    .withColumn("cover", F.regexp_extract("pages", r",\s*(.*)$", 1)) \
    .withColumn("publish", F.to_date(F.regexp_extract(col("publish"), r'(\w+ \d{1,2}, \d{4})', 1), "MMMM d, yyyy")) \
    .drop("pages")



# Insert data into PostgreSQL
def insert_data(df):
    query = df.writeStream \
        .outputMode("append") \
        .foreachBatch(lambda batch_df, batch_id: write_batch_to_postgres(batch_df)) \
        .start()
    query.awaitTermination()

def write_batch_to_postgres(batch_df):
    with psycopg2.connect(
        dbname='goodread',
        user='admin',
        password='admin',
        host='postgres',
        port='5432'
    ) as conn:
        with conn.cursor() as cur:
            # Tách dữ liệu từ batch_df cho từng bảng
            author_df = batch_df.select("author_id", "author").distinct()
            ratings_df = batch_df.select("book_id", "rating", "fivestars", "fourstars", "threestars", "twostars", "onestar").distinct()
            book_df = batch_df.select("book_id", "bookname", "author_id", "prices", "describe", "pages_n", "cover", "publish", "rating", "ratingcount", "reviews", "author", "genre").distinct()
            describe_df = batch_df.select("book_id", "author_id", "describe", "bookUrl").distinct()

            # Chèn dữ liệu vào từng bảng
            insert_authors(cur, author_df)
            insert_ratings(cur, ratings_df)
            insert_books(cur, book_df)
            insert_describes(cur, describe_df)
            conn.commit()

# Hàm để chèn dữ liệu vào bảng Author
def insert_authors(cur, author_df):
    authors = author_df.collect()  # Thu thập dữ liệu từ DataFrame
    for row in authors:
        cur.execute(
            "INSERT INTO Author (author_id, author) VALUES (%s, %s) ON CONFLICT (author_id) DO NOTHING;",
            (row['author_id'], row['author'])
        )

# Hàm để chèn dữ liệu vào bảng Rating
def insert_ratings(cur, ratings_df):
    ratings = ratings_df.collect()  # Thu thập dữ liệu từ DataFrame
    for row in ratings:
        cur.execute(
            """
            INSERT INTO Rating (book_id, rating, fivestars, fourstars, threestars, twostars, onestar)
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (book_id) DO NOTHING;
            """,
            (row['book_id'], row['rating'], row['fivestars'], row['fourstars'],
             row['threestars'], row['twostars'], row['onestar'])
        )

# Hàm để chèn dữ liệu vào bảng Book
def insert_books(cur, book_df):
    books = book_df.collect()  # Thu thập dữ liệu từ DataFrame
    for row in books:
        cur.execute(
            """
            INSERT INTO Book (book_id, author_id, rating, genre, describe, author, bookname, publish, prices, ratingcount, quantity, pages_n, cover)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (book_id) DO NOTHING;
            """,
            (row['book_id'], row['author_id'], row['rating'], row['genre'] ,row['describe'], row['author'],
             row['bookname'], row['publish'], row['prices'], row['ratingcount'], row['reviews'],
             row['pages_n'], row['cover'])
        )

# Hàm để chèn dữ liệu vào bảng Describe
def insert_describes(cur, describe_df):
    describes = describe_df.collect()  # Thu thập dữ liệu từ DataFrame
    for row in describes:
        cur.execute(
            """
            INSERT INTO Describe (book_id, author_id, describe, bookUrl)
            VALUES (%s, %s, %s, %s) ON CONFLICT (book_id, author_id) DO NOTHING;
            """,
            (row['book_id'], row['author_id'], row['describe'], row['bookUrl'])
        )


# Chạy chương trình
insert_data(cleaned_df)
spark.stop()