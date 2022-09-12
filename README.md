# 1 - Clone the repository with the following command:
git clone https://github.com/Alfonso00MA/frtrs-assignment.git

# 2 - Modify frtrs-assignment/app/weatherapi_key accordingly to use your weatherapi key:
vim frtrs-assignment/app/weatherapi_key

# 3 - Start application up. (You might need sudo)
make up

# 4 - At this point you can test the different API endpoints:
#
# http://127.0.0.1:82/life_expectancy/{sex}/{race}/{year}
# http://127.0.0.1:82/unemployment/{state}
# http://127.0.0.1:82/trends?phrase=[phrase]&start_date=[date]&end_date=[date]
# http://127.0.0.1:82/weather
# http://127.0.0.1:82/trends_weather?phrase=[phrase]

# A few examples:
# http://127.0.0.1:82/life_expectancy/Female/Black/1999
# http://127.0.0.1:82/unemployment/Ohio
# http://127.0.0.1:82/trends?phrase=Rusia&start_date=2022-01-01&end_date=2022-02-02
# http://127.0.0.1:82/weather
# http://127.0.0.1:82/trends_weather?phrase=bitcoin

# To run the tests (You might need sudo):
make test
