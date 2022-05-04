This project is meant to show difference in time execution between the same databases placed locally, in the docker or in a cloud.\
There are three operations for which we will measure time execution: inserting, selecting and clearing. 

### What should I do to get it ready?

1. Make sure to have all three databases (local, docker, cloud) working and available to connection from outside.
2. Make sure to have a table called 'test-table' in each of these databases.
3. All grid-tables should have three columns: id (serial, Primary Key, not null), integer (integer, not null), string (text, not null).
4. Make sure these tables are empty or at least don't have anything important inside, because after program execution they will become empty.
5. In \_\_main__.py find a variable 'credentials_list'. Fill it with right data (only dbnames, hosts and ports if you followed this instruction).
6. Your program is ready.

Note: You can ignore/change some of these actions if you know what you're doing.

### Insertion

This operation inserts 1000 (by default) rows into table. Each row has a format like: (i, rand_int, some_text). It doesn't matter anyway what's inside them. What's matter — it's the speed of inserting.\
You can change number of inserted rows by changing the variable 'number_of_rows' or data inserted by changing the variable 'data' both inside '\_insert' function in \_\_main__.py.

### Selection

This operation has two variations by default: select all rows and select by condition ("'test-table'.integer > 120" by default).\
You can change it by changing variables operations_list, functions_list and args_list inside main function in \_\_main__.py.

### Clearing

This operation simply removes all rows from the table.

### How program works

There is also a variable called 'number_of_tests' inside main function in \_\_main__.py. You can use this variable to get more reliable results, but it will take more time to get them.\
For each database tested we launch number_of_tests tests. In each of them we sequentially run functions insert, select (both all and by condition versions) and clear.\
For each of the operation and each of the database we measure total time, which was taken to execute this operation on this database during all tests.\
Then results converted into pandas DataFrame and it's shown in the console.
