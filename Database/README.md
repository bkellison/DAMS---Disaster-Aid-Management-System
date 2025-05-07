# database schema

# Add schema file to project
1. After connecting --> Server --> Data Export
2. Select the Schema --> Dump Structure (make sure you select stored procedures)
3. Remember to un-select any unwanted tables/views you may have created.
4. Once dumped, rename `DatabaseV{NEXT_VERSION}Team3`
5. Copy file into this project file

Goal is we'd have a new final each time we updae the schema, so we have a history and can easily revert



# Import new schema into MySql
1. After connecting --> Server --> Data Import
2. Confirm your file path points to the correct folder in this project
3. Start Import