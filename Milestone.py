import radb
import sqlparse
import sql2ra

stmt = "select distinct A.name, B.name from Eats A where A.pizza = B.pizza"

stmt = sqlparse.parse(stmt)[0]

stmt = sql2ra.Translate(stmt)

print(stmt)