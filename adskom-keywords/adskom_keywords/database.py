#!/usr/bin/env python

from __future__ import absolute_import, division, with_statement

import copy
import itertools
import logging
import os
import time
import pymysql

version = "0.1"
version_info = (0, 1, 0, 0)

class Connection(object):
    """A lightweight wrapper around PyMySQL DB-API connections.

    The main value we provide is wrapping rows in a dict/object so that
    columns can be accessed by name. Typical usage::

        db = database.Connection("localhost", "mydatabase")
        for article in db.query("SELECT * FROM articles"):
            print article.title

    Cursors are hidden by the implementation, but other than that, the methods
    are very similar to the DB-API.

    We explicitly set the timezone to UTC and the character encoding to
    UTF-8 on all connections to avoid time zone and encoding errors.
    """
    
    Prefix = ''
    QueryResult = {}
    insert_id = ""
    rowcount = 0
    field='*'
    
    def __init__(self, host, database, user=None, password=None,
                 max_idle_time=7 * 3600):
        self.host = host
        self.database = database
        self.max_idle_time = max_idle_time

        args = dict(use_unicode=True, charset="utf8",
                    db=database,
                    sql_mode="TRADITIONAL")
        if user is not None:
            args["user"] = user
        if password is not None:
            args["password"] = password

        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306

        self._db_init_command = 'SET time_zone = "+0:00"'
        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error("Cannot connect to MySQL on %s", self.host,
                          exc_info=True)

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = pymysql.connect(autocommit=True, **self._db_args)
        self.execute(self._db_init_command)

    def iter(self, query, *parameters):
        """Returns an iterator for the given query and parameters."""
        self._ensure_connected()
        cursor = self._db.cursor(buffered=True)
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            for row in cursor:
                yield Row(zip(column_names, row))
        finally:
            cursor.close()

    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(zip(column_names, row)) for row in cursor]
        finally:
            cursor.close()

    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    

    # rowcount is a more reasonable default return value than lastrowid,
    # but for historical compatibility execute() must return lastrowid.
    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
#         print(query)
#         print(*parameters)
        return self.execute_lastrowid(query, *parameters)

    def execute_lastrowid(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, query, *parameters):
        """Executes the given query, returning the rowcount from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self._db is None or
                (time.time() - self._last_use_time > self.max_idle_time)):
            self._last_use_time = time.time()
            self.reconnect()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters):
        try:
            return cursor.execute(query, parameters)
        except pymysql.OperationalError:
            logging.error("Error connecting to MySQL on %s", self.host)
            self.close()
            raise
        
    def prepare_insert_statement(self,table,data={},ignore=False,escapeencode = {},unquote ={},debug = False) :
        ky = []
        val = []
        values = []
        param = {}
        i = 0;
        for key, value in data.items():
            quote = False if key in unquote else True
            escape = False if key in escapeencode else True
            ky.append(key)
            if isinstance(value, str) :
                values.append(self._tosql( value.strip(),'Text',quote,escape))
            else :
                values.append(self._tosql( value,'Number',quote,escape))

            
        table = self._fixtable(table)
        if(ignore == True) :
            ins = "INSERT IGNORE INTO "+table+" ("+','.join(ky)+") VALUES ("+','.join(values)+")"
        else :
            ins  = "INSERT INTO "+table+" ("+','.join(ky)+") VALUES ("+','.join(values)+")"
            
        return ins
    
    def prepare_update_statement(self,table,data={},condition=None,prepare={},escapeencode = {},unquote ={},debug = False):
        val = []
        param = {}
        values = []
        for key, value in data.items():
            quote = False if key in unquote else True
            escape = False if key in escapeencode else True
            
            if isinstance(value, str) :
                values.append(key +' = ' + self._tosql( value.strip(),'Text',quote,escape))
            else :
                values.append(key +' = ' + self._tosql( value,'Number',quote,escape))
                
        table = self._fixtable(table)
        if isinstance(condition, str) == True :
            param.update(prepare)
            where = condition
        else :
            params = self._where(condition)
            where = params['where']
            param.update(params['param'])

        query  = "UPDATE "+table+" SET "+' , '.join(values)+" "+ where
        return query

        
    def _tosql(self,value, type,quote = False,encode = True):
        if(value == "" and value != 0):
            return "NULL"
        else  :
            if(type == "Number") :
                return float(value)
            else:
                if(encode == True) :
                    value = self._htmlspecialchars(value)
                if(quote == False):
                    return value
                else :
                    return "'" +value+ "'"

    def _fixtable(self,table_param):
        table_param = str(table_param)
        if (self.Prefix != ''):
            if "#__" in table_param:
                table = string.replace(table_param, "#__", self.Prefix)
            else :
                table = self.Prefix+table_param
        else :
            table = table_param
        return table

    def _where(self, condition = {},escapeencode = {},unquote ={}):
        where = ""
        param = {}
        if len(condition) > 0 :
            where += "where "
            i = 0
            for key in condition :
                value = condition[key]
                i += 1
                word = key.strip()
                word_get = word.rsplit(' ',1)
                key = word_get[0].strip()
                if len(word_get) == 2 :
                    operator = word_get[1]
                else :
                    operator = "="
                if isinstance(value, str) :
                    where += "  "+str(key)+" "+operator+" "+ value 
                else:
                    where += "  "+str(key)+" "+operator+" "+ value 
                    
                if i > 0 and i < len(condition):
                    where += " and "
                param[key] = value
        else:
           param = condition
        return {"where":where,'param':param}

    def _field(self,required= []):
        if len(required) > 0 :
            fields = ""
            i = 0
            for field in required :
                i += 1
                fields += " "+str(field)
                if i < len(required) :
                    fields += ", "
            self.field = fields

    def _htmlspecialchars(self,text):
        return (
            text.replace("&", "&amp;").
            replace('"', "&quot;").
            replace("<", "&lt;").
            replace(">", "&gt;")
        )


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
