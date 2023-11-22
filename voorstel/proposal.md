## Korte introductie van pair-trading
Een voorbeeld hiervan is LONG AAPL en SHORT TSLA. Het voordeel van pairtrading is dat je je directional risk minimaliseert. Dus als de markt omhoog gaat, dan verlies je op je short, maar door middel van goede position sizing zou je evenveel geld moeten maken met de long positie. 
Het is alleen een aardig wiskundig proces om de sizing goed te krijgen, maar gelukkig is een computer daar heel goed in. 
Ik wil pair-trading nog een stap verder nemen. 

*Basket-trading* 

Laten we zeggen dat er een narrative is ontstaan. Bijvoorbeeld AI door een OpenAI conference. Markt participanten willen exposure naar AI assets. De markprijzen van de AI sector assets zijn mega hard gestegen. Skip forward een aantal weken. Je denkt dat het AI narrative tot zijn einde gekomen is. De volgende conference is van een marktleider in de Big Data sector. Je denkt dat er het zelfde gaat gebeuren en dat de vraag naar Big Data assets gaat stijgen in de markt en tegelijkertijd denk je dat de AI sector interesse verliest. Dit maakt een perfecte kans voor een basket trade. 
We gaan LONG op de assets van Big Data en we gaan SHORT op de assets van AI. Bereken de juiste size per positie en vervolgens ben je Delta Neutral (geen directional risk). 

*Synthetic Tickers*

Alle traders en investors kijken naar de grafiek van de asset die ze handelen. Het mooie van pair- en basket trading is dat ze ook hun eigen grafiek krijgen.
Van het bovenstaande voorbeeld zou het er als volgt uitzien. 

Stock1: Big Data
Stock2: Big Data
Stock3: Big Data

Stock4: AI
Stock5: AI
Stock6: AI

Synthetic Ticker = (Stock1 * Stock2 * Stock3)^0.33 / (Stock4 * Stock5 * Stock6)^0.33 (I)

Hiermee kan je dus ook visualizeren hoe verschillende sectors tegen elkaar traden. Dit is enorm waardevolle informatie voor investors en traders. 



## Wat is het probleem

Het probleem is dat Pair Trading en Basket Trading bijna niet toegankelijk is voor traders en investors. Synthetic tickers zijn alleen te maken met peperdure Tradingview (charting software) abonnementen en er is verder geen platform dat dit toelaat. Daarbij komt het feit dat de meeste mensen dus ook geen inzage kunnen krijgen naar sector performance. Als je dit zou willen doen moet je betalen of je eigen programma maken.


## Verwachte gebruikers

Dit zouden vooral traders en handelaren zijn die geinteresseerd zijn in een inzage van relative performance van sectors in de markt. Ik ken meerdere mensen vanuit mijn netwerk die zich bezig houden met pair traden omdat het een van de meest veilige manieren van traden is. 
Mijn platform zou ook te gebruiken zijn voor mensen die zich niet bezig willen houden met Pair Trading en Basket Trading, maar simpelweg willen inzien hoe een bepaalde sector zich gedraagt in de markt. Door de noemer in vergelijking I te veranderen naar een index asset zoals SPX of BTC, kan je de relatieve performance van die sector zien. Je kan zelfs de rotatie tussen sectors visualizeren door meerdere synthetic tickers te plotten. 

## Welke setting?

Dit zou vooral op een laptop scherm bekeken worden. Er is ook configuratie nodig; denk aan timeframe, tickers, sectors en grafiek soort (lijn of candles).


## Mijn oplossing

Ik wil een dashboard maken waar mensen hun eigen synthetic tickers kunnen creëren en op een grafiek kunnen zetten. Ik wil dat er meerdere synthetic tickers opp 1 chart kunnen komen. Ik wil dat mensen een account kunnen maken en een lijst met favoriete tickers kunnen opslaan, zodat ze die snel kunnen plotten. Ik wil een calculator maken die de size per positie aan kan geven om zo dicht mogelijk bij delta neutral te komen. Ik ben vooral bezig met cryptocurrencies en in mijn ervaring spelen sectors een grotere rol in crypto dan in traditional markets, dus ik wil v1 bouwen voor crypto en mogelijk later doorschalen naar alle markten. Ik denk na om een mogelijkheid te maken dat je je exchange API keys kan opslaan, zodat je de trade kan maken vanuit mijn platform. 


## Hoe zou het eruit zien?
Dit zijn alleen schetsen natuurlijk.

De home page:
![Home](voorstel/pictures/home.jpg)

De register page:
![Register](voorstel/pictures/register.jpg)

De login page:
![Login](voorstel/pictures/login.jpg)

De charting page:
![Charting](voorstel/pictures/charting.jpg)

De 'Your own basket' page:
![Your own basket](voorstel/pictures/own_basket.jpg)

De calculator page:
![Calculator](voorstel/pictures/calculator.jpg)