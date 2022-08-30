from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_life_expentancy():
    response = client.get("/life_expectancy/Female/Black/1999/")
    assert(response.status_code == 200)
    assert(response.json() == {"average_life_expectancy": 74.7})
    
    response = client.get("/life_expectancy/Female/Black/10/")
    assert(response.status_code == 200)
    assert(response.json() == {"average_life_expectancy": None})
    

def test_unemployment():
    response = client.get("/unemployment/Ohio/")
    assert(response.status_code == 200)
    assert(response.json() == {"rate":"3.9"})
    
    response = client.get("/unemployment/RandomString")
    assert(response.status_code == 422)
    assert(response.json() == {"detail":[{"loc":["path","state"],"msg":"value is not a valid enumeration member; permitted: 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'","type":"type_error.enum","ctx":{"enum_values":["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]}}]})
    
    
def test_trends():
    response = client.get("/trends?phrase=Rusia")
    assert(response.status_code == 200)
    assert(10 < len(response.json()["interest"]) <= 11) # TODO confirm that this works fine on both: weekdays and weekends
    
    response = client.get("/trends?phrase=Rusia&start_date=2010-01-01&end_date=2010-02-02")
    assert(response.status_code == 200)
    assert(response.json() == {"interest":[66,54,74,68,67,70,80,77,91,77,88,81,82,80,88,82,75,90,94,91,96,72,95,82,88,98,83,100,87,83,83,85,86]})
    
    response = client.get("/trends?phrase=Rusia&start_date=2010-02-02&end_date=2010-01-01")
    assert(response.status_code == 400)
    assert(response.json() == {"detail":"Start date later than end date"})

def test_weather():
    response = client.get("/weather")
    assert(response.status_code == 200)
    assert(len(response.json()["weather"]) == 8) 