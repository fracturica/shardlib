# Shardlib

[![Build Status](https://travis-ci.org/fracturica/shardlib.svg?branch=master)](https://travis-ci.org/fracturica/shardlib)

**Shardlib is a collection of Python modules aimed at the analysis of Policrack databases. It provides the functionality for the Enrupture analysis framework.**

Copyright &copy; 2012 - 2014, 2017 Dimitar Danov<br>
Copyright &copy; 2012 - 2014, 2017 Prof. Mario Guagliano<br>
Distributed under the terms of MIT License.


## Overview

Shardlib provides the functionality for the Enrupture analysis framework for Policrack databases.

It provides a database management system for Policrack databases, analytical solutions, data transformation, session persistence, plotting and interactivity features.

Shardlib has been used at a scale of 10s of thousands of database records.


## Features

Shardlib provides the following functionality:
- Database management system including:
  - database discovery;
  - index creation;
  - record retrieval;
  - database query.
- Data transformation and aggregation.
- Analytical solutions for embedded elliptic cracks.
- Session storage.
- Interactivity.
- Plot generation.
- Logging.


### Database Management

The `shardlib` database management provides an abstraction layer that hides the complexity of dealing with multiple databases in a Policrack repository by presenting them as a single database.
This is achieved by creating a unique id for each record called `simId`.

A `simId` is a combination of the database name and the record key in the database. It solves two problems. First, of potential name collisions (database names are unique and record keys are unique within a database). Second, the system can easily identify the database in which the record is stored, without searching all databases.


#### Database Discovery

Shardlib looks for a Policrack database repository in a directory named `db`. The directory structure is as follows:
<pre>root
├ db
| ├ database_1
| ├ ...
| └ database_n
└ application_directory
  └ shardlib</pre>
The `db` directory is the Policrack database repository and `shardlib` is the directory of the library and `application_directory` is the directory of the application.


#### Index

Shardlib can create an index (tree data structure) of the discovered databases. It is created at the beginning of every analysis and is not persistent between sessions.


#### Queries

Both table scan and index queries are supported and distinguished from one another. Index queries are tree searches. Table scan queries scan all the databases.

In practice, once the index is generated, most queries use a combination of both index search and table scan of a subset of the databases.


#### Record Retrieval

Record retrieval is performed using a `simId`, which contains the database name and the record key in the database.


### Data Transformation and Aggregation

Shardlib can calculate estimates of a single record and filter its data. Data from multiple records can be combined and same filters and estimates can be applied to the aggregate data.


### Analytical Solutions

Analytical solutions for stress intensity factors for an embedded elliptic crack under remote load use the definitions from:

`B. Nuller, E. Karapetian, and M. Kachanov. On the stress intensity factor for the elliptical crack. International Journal
of Fracture, 92(2):15–20, 1998`


### Session Storage
Session storage is a persistent storage of `simId`s. It addresses the following two scenarios:
 - exclusion of records from further considerations without writing to the Policrack database.
 - earmarking `simId`s for further analysis.


### Interactivity

The interactivity feature is a non-persistent queue, to which `simId`s can be added, removed and retrieved in subsequent operations.


### Plots

Shardlib can generate specialized plots for analysis and visualization of data from a single database record or multiple records.

- __Color Maps (Contour Plots)__ &mdash; container size convergence analysis.

- __3D Scatter Plots__ &mdash; visualization of the XFEM mesh parameters.


- __Box Plots__ &mdash; distribution of the data and calculated errors.
Box plots are used in two modes &mdash; a single record and multiple records.
  - _single record mode_ &mdash; each box of the plot represents data from a single record;
  - _multiple records mode_ &mdash; each box represents data collected from multiple records.

- __Line Plots__ &mdash; plot of the data points from a single or multiple records.

- __Histogram__ &mdash; histogram of the data points from multiple records.

- __Range Plot__ &mdash; visualization of data points from multiple records, organized in bins and overlaid with the actual data points and a line plot of a selected record.

- __Bounds Plot__ &mdash; visualization of the data points from multiple records and lines representing upper and lower bound for the data.


### Logging

Most operations with `shardlib` use print statements to display feedback information.


## Installation

The recommended approach is to install the library manually and vendorize the library. [Database discovery](#database-discovery) requires a certain directory structure to work.


## Security Warning

Shardlib uses Python shelves for persistence and reads Policrack databases, which are also shelves.

**Only use trusted sources for Policrack databases and `shardlib` persistence objects**


### Requirements

Shardlib is designed to work with Python 2.7 and requires `numpy`, `scipy` and `matplotlib`.


## Further Development

Shardlib does what we wanted it to do, when we started. It has been a positive experiment and we do not plan further updates at present.
