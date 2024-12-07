import logging
from myapp import APP
import mydb

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
  mydb.connect()
  APP.run(host='0.0.0.0', port=9001)

