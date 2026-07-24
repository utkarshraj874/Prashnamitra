import psycopg2
conn = psycopg2.connect("dbname=interview_simulator user=postgres password=manish123 host=localhost port=5432")
print("Connected OK")
