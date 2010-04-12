#!/bin/bash

ME=`whoami`

if [ $ME == "root" ]; then

  echo "] Installing BlueDarD..."
  cp ./bluedard /etc/rc.d/bluedard
  chmod 755 /etc/rc.d/bluedard
  cp BlueDarD.py /usr/bin/BlueDarD.py

  RESULT=`python TEST.py`

  if [ $RESULT -eq 0 ]; then

	  print "] Installing pyrssi..."
	  cd pyrssi && python setup.py build && python setup.py install

  fi

fi
