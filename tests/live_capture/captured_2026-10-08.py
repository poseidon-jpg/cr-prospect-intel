"""Live payloads captured 2026-10-08 through a real browser (Claude in Chrome) because the build sandbox has no
open egress. JSON bodies are verbatim; TikTok embed states are the verbatim fields the parser reads
(userInfo + videoList id/playCount/desc; captions truncated to 50-55 chars by the capture tool)."""
DNS_TXT_LIQUIDDEATH = {"Status":0,"Answer":[{"type":16,"data":d} for d in [
 "google-site-verification=FiXFP5CkhoQ6saGzeYDUuSiu1XVEGrLoRgRsbu-JWoc","apple-domain-verification=YG4KaL30JuuW2oQY",
 "anthropic-domain-verification-kgfyr5=kwDOWqjhyZAhw8vE1Pk8s9jWh","dropbox-domain-verification=ye1fwjwaq2oy",
 "zapier-domain-verification-challenge=ab390b33-b47e-4d2e-9488-589c745ab41d","google-site-verification=TPEJ6Z2blNJ92dJ7cJViXQTnaZvnxM1-GAqRetSIuRc",
 "google-site-verification=isfKqiY2YKaGYEy_IKkwL7Nqbji-dcWHz--AqC43jYw","klaviyo-site-verification=Y2F9HV","klaviyo-site-verification=Ntc5BJ",
 "klaviyo-site-verification=RgZw9i","google-site-verification=jyjV_YX9tyF-5M0goYvB3j9ib1EiB7pdn-Qf-G6YhhU","klaviyo-site-verification=Vi2cjW",
 "slack-domain-verification=liRACbSIjBd8jw7OI0UbMsqIS7Q8tjrKtdAk9tsq","MS=ms18077185","v=spf1 include:_spf.liquiddeath_com._d.easydmarc.pro -all",
 "openai-domain-verification=dv-ynhIfNrVDZApjhFjN8gYLp0y","klaviyo-site-verification=VAewSJ",
 "atlassian-domain-verification=EDmaEz5A29buAzEmLTgI3At6dv3bwZ2DuakZG634RYauBqZqdz9OXutw5B/aGpm4",
 "mailerlite-domain-verification=0252aa3c6ecb147e4b448f838b1f157d3aaa6ac8","apple-domain-verification=lKzEtOkUCCkacSl0o61wWcqZouUUGXuH6_DNnCQxCw0",
 "E358694DFB","airtable-verification=f9570965d9f0f9c4acc3f4cc849037c4"]]}
DNS_MX_LIQUIDDEATH = {"Status":0,"Answer":[{"type":15,"data":d} for d in ["10 alt3.aspmx.l.google.com.","1 aspmx.l.google.com.","5 alt1.aspmx.l.google.com.","10 alt4.aspmx.l.google.com.","5 alt2.aspmx.l.google.com."]]}
DNS_DMARC_LIQUIDDEATH = {"Status":0,"Answer":[{"type":16,"data":"v=DMARC1; p=quarantine; sp=quarantine; rua=mailto:re+aee5069b64fe@inbound.dmarcdigests.com; pct=100"}]}
WD_SEARCH_LIQUIDDEATH = {"search":[{"id":"Q106254248","label":"Liquid Death","description":"canned water company"},{"id":"Q134585034","label":"Liquid Death","description":"1953 novel by John Russell Fearn"}],"success":1}
WD_ENTITY_Q106254248 = {"entities":{"Q106254248":{"labels":{"en":{"language":"en","value":"Liquid Death"}},"descriptions":{"en":{"language":"en","value":"canned water company"}},"claims":{"P856":[{"mainsnak":{"datavalue":{"value":"https://liquiddeath.com"}}}],"P2002":[{"mainsnak":{"datavalue":{"value":"LiquidDeath"}}}],"P2003":[{"mainsnak":{"datavalue":{"value":"liquiddeath"}}}],"P2397":[{"mainsnak":{"datavalue":{"value":"UCpRMG5MU1RurWtdiRFtPyvQ"}}}],"P7085":[{"mainsnak":{"datavalue":{"value":"liquiddeath"}}}],"P2013":[{"mainsnak":{"datavalue":{"value":"DrinkLiquidDeath"}}}],"P4264":[{"mainsnak":{"datavalue":{"value":"liquid-death"}}}],"P159":[{"mainsnak":{"datavalue":{"value":{"entity-type":"item","numeric-id":65,"id":"Q65"}}}}]}}}}
WD_ENTITY_Q134585034 = {"entities":{"Q134585034":{"labels":{"en":{"value":"Liquid Death"}},"descriptions":{"en":{"value":"1953 novel by John Russell Fearn"}},"claims":{}}}}
WD_LABELS = {"entities":{"Q65":{"labels":{"en":{"value":"Los Angeles"}}}}}
GREENHOUSE_LIQUIDDEATH = {"jobs":[],"meta":{"total":0}}
OEMBED_EXISTS = {"liquiddeath":"Liquid Death","liquiddeathfan":"LiquidDeathFan","boxabl":"BOXABL","boxablclips":"boxablclips",
 "boxablclip":"Boxabl Clip 🏠","boxablclipz":"boxablclipz","boxablmoments":"BOXABL Moments","boxablhighlights":"boxabl records",
 "boxabldaily":"boxabldaily","boxablnews":"BoxablNews","boxablfans":"boxablfans","boxablfan":"Boxabl Tiny Homes"}
OEMBED_MISSING = ["boxabledits","boxabledit","boxablhq","boxabltv","boxablfanpage","boxablupdates","boxablmedia","boxablpod","boxablpodcast","boxablshow",
 "liquiddeathclips","liquiddeathclip","liquiddeathedits","liquiddeathmoments","liquiddeathdaily","liquiddeathhq","liquiddeathnews","liquiddeathfans",
 "liquiddeathofficial","theliquiddeath","drinkliquiddeath","getliquiddeath","liquiddeathugc","liquiddeathreviews","liquiddeathmemes"]
EMBED = {
 "boxabl": ({"followerCount":114400,"heartCount":636200,"followingCount":293,"verified":False,"nickname":"BOXABL","signature":"🏠Housing meets mass production 🏭 \n\nBOXABL is now trading on the stock market \nNasdaq ticker $BXBL \nRead disclaimers boxabl.com/ir","privateAccount":False},
   [["7052108180268059905",68900],["7030470638716472578",52900],["6903711420026735874",3200000],["7677735976105430293",2516],["7674050137399889172",2187],["7672932985221549333",1786],["7672563465894071573",1577],["7670704222484188437",1445],["7668755545087692052",1835],["7657353520177351957",4587],["7656975322646056212",3271],["7650674156341644564",158100],["7650288005097295125",3164]],
   ["A foldable house?! ONLY $50,000!? We plan to help billi","Everyone deserves an affordable #home","Housing meets mass production... #tinyhouse #factory #e","🤣","Would you live in this foldable home? #adu ","Delivering a two bedroom Casita in California #fyp #cas","BOXABL Casita delivered to Sacramento! #fyp #casita ","A home delivered to you, fast.","Installing a two bedroom Casita in one day 📦➡️🏠","A home delivered to you. Unpacked in one day. #fyp","Rate 1-10 #fyp #casita ","Would you live in a BOXABL?","Would you live in a BOXABL Casita? "]),
 "boxablclips": ({"followerCount":106,"heartCount":6360,"verified":False,"nickname":"boxablclips","signature":"Boxabl is the FUTURE of HOUSING! Invest Now!"},
   [["7287558105318100270",108],["7287466318511787310",84],["7287307288442866987",262],["7287264339097095467",115],["7287174600012647726",251],["7287123823613316395",90],["7286714141883092267",72],["7286443428093840686",88],["7286269241441946922",42],["7285770490222791978",222]],
   ["Boxabl Is Taking Over The Housing Industry! 🗝️  #","Boxabl Is Taking Over The Housing Industry! 🏡  #B","Boxabl Is Taking Over The Housing Industry! 🏡  #B","Boxabl Is Taking Over The Housing Industry! ⚜️  #B","Boxabl Is Taking Over The Housing Industry! 🗝️  #","Boxabl Is Taking Over The Housing Industry! 🚪  #B","Boxabl Is Taking Over The Housing Industry! ⚜️  #B","Boxabl Is The FUTURE Of Housing! #house #invest","Boxabl Is Taking Over The Housing Industry! #Boxab","Boxabl Is Taking Over The Housing Industry! #Boxab"]),
 "boxablclip": ({"followerCount":0,"heartCount":0,"verified":False,"nickname":"Boxabl Clip 🏠","signature":"The best Boxabl home videos\n🏠 Affordable modular homes"},[],[]),
 "boxablmoments": ({"followerCount":1,"heartCount":95,"verified":False,"nickname":"BOXABL Moments","signature":"best moments from the company @BOXABL"},
   [["7687957513945287949",423],["7686872770164133150",1003],["7686598927423933726",1296]],
   ["the founder vs the foundation of the BOXABL Casita","@BOXABL is the future of affordable housing😮‍💨 #","richest man alive owns the BOXABL Casita which cos"]),
 "boxabldaily": ({"followerCount":10,"heartCount":764,"verified":False,"nickname":"boxabldaily","signature":"The future of housing"},
   [["7262244064458755370",39],["7262218044720680234",49],["7262192608586321194",16],["7262126779769343274",73],["7262126051751480618",82],["7262060329213922603",77],["7261967746408140074",92],["7261888379225148714",13],["7261650692367027498",79],["7261635414832909614",85]],
   ["Boxabl is TAKING OVER the HOUSING Industry (you ca"]*10),
 "boxablnews": ({"followerCount":54,"heartCount":525,"verified":False,"nickname":"BoxablNews","signature":"Latest News On Boxabl!"},
   [["7262165375733763370",39],["7262059201692847403",122],["7261790602335931691",23],["7261740398727531819",86],["7261649978219695403",24],["7261649164927356203",18],["7261646089164442923",22],["7261589953371540782",234],["7261540544076336430",51],["7261392414508666155",165]],
   ["Boxabl is TAKING OVER the HOUSING Industry (you ca"]*10),
 "liquiddeath": ({"followerCount":7300000,"heartCount":23700000,"followingCount":222,"verified":True,"nickname":"Liquid Death","signature":"Don’t be scared. It's just a better-for-you beverage company."},
   [["7690988314677005598",474500],["7680599033039179038",8192],["7675355923765873934",4600000],["7672806702537821454",12900],["7670207549106375967",374700],["7667610861657197854",13500],["7667242688076401951",12000],["7662786640150088990",4400000],["7662046156125474079",1300000],["7657226490446122271",14000]],
   ["This Halloween, don't drink blood. Drink Blood Zer","We agree. Drinking and driving is very bad. Good t","We want your pee. Please give us your pee.  And ma","New @goodwipes x Liquid Death Cream Soda scented w","Liquid Death teamed up with Feastables and MrBeast","🚨NEW Raspberry Rage Iced Tea exclusively at Walma","The official coloring book of Liquid Death, illust","Liquid Death Energy can't actually make you fly, b","🚨NEW Cinnamon Roll Iced Tea now on Amazon🚨  It’s","Our longtime friend and skateboarder turned standu"]),
}
