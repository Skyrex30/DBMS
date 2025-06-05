MongoDB DBMS

  A custom database management system built on top of MongoDB with a Flask REST API. This project implements a relational database-like interface over MongoDB, providing features like foreign key constraints, unique constraints, custom indexing, and advanced query operations.
  Features
  Core Database Operations

  Database Management: Create, drop, and list databases
  Table Management: Create, drop, and list collections (tables)
  CRUD Operations: Insert, delete, and select rows with validation
  Bulk Operations: Efficient bulk insert with batch processing

Advanced Features

  Constraint Validation: Primary keys, foreign keys, and unique constraints
  Custom Indexing: Unique and non-unique indexes with automatic maintenance
  Advanced Queries: Complex SELECT operations with joins, GROUP BY, and aggregations
  Join Strategies: Hash Join and Index Nested Loop Join (INLJ)
  Aggregation Functions: COUNT, SUM, AVG, MIN, MAX with GROUP BY and HAVING clauses
  Transaction Support: ACID compliance for data operations

Query Capabilities
  
  Filtering: Support for various operators (=, >, >=, <, <=)
  Sorting: ORDER BY with ASC/DESC support
  Joins: Inner joins between tables with optimized strategies
  Projections: Select specific columns or all columns
  Aggregation: GROUP BY with aggregate functions (COUNT, SUM, AVG, MIN, MAX)

Installation
Prerequisites

  Python 3.7+
  MongoDB 4.0+
  Flask
  PyMongo
