#!/bin/sh
kill `ps ax | grep runserver | grep manage | awk '{print $1}'`
