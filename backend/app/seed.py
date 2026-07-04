from google.cloud.firestore_v1.client import Client

DESTINATIONS = [
    dict(
        id="jaipur",
        name="Jaipur",
        country="India",
        region="Asia",
        description=(
            "Known as the Pink City for the terracotta hue of its old-town facades, Jaipur is the "
            "capital of Rajasthan and a showcase of Rajput architecture. Its 18th-century City Palace, "
            "the astronomical instruments of Jantar Mantar, and the honeycomb windows of Hawa Mahal sit "
            "alongside bustling bazaars selling block-printed textiles, gemstones, and leather juttis."
        ),
        image_url="https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
        lat=26.9124,
        lng=75.7873,
        tags=["heritage", "architecture", "food", "shopping", "palaces"],
    ),
    dict(
        id="kyoto",
        name="Kyoto",
        country="Japan",
        region="Asia",
        description=(
            "Japan's imperial capital for over a thousand years, Kyoto holds more than 1,600 Buddhist "
            "temples and 400 Shinto shrines, from the golden pavilion of Kinkaku-ji to the vermillion "
            "torii tunnels of Fushimi Inari. Geisha still cross the lantern-lit lanes of Gion at dusk, "
            "and centuries-old ryokan and kaiseki traditions endure alongside a living tea-ceremony culture."
        ),
        image_url="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
        lat=35.0116,
        lng=135.7681,
        tags=["temples", "gardens", "tea-ceremony", "history", "food"],
    ),
    dict(
        id="marrakech",
        name="Marrakech",
        country="Morocco",
        region="Africa",
        description=(
            "A red-walled imperial city at the foot of the Atlas Mountains, Marrakech centers on the "
            "chaotic theatre of Jemaa el-Fnaa square, where snake charmers, storytellers, and food stalls "
            "come alive at night. Its medina hides ornate riads, the Bahia Palace, and the Majorelle "
            "Garden, while souks overflow with leather, spices, and hand-woven carpets."
        ),
        image_url="https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?auto=format&fit=crop&w=1200&q=80",
        lat=31.6295,
        lng=-7.9811,
        tags=["souks", "architecture", "desert-gateway", "food", "crafts"],
    ),
    dict(
        id="oaxaca",
        name="Oaxaca",
        country="Mexico",
        region="North America",
        description=(
            "Set in a highland valley in southern Mexico, Oaxaca de Juarez is a UNESCO World Heritage "
            "city celebrated for its baroque Santo Domingo church, vibrant indigenous Zapotec and "
            "Mixtec heritage, and a culinary scene anchored by mole, mezcal, and tlayudas. Nearby ruins "
            "at Monte Alban and the annual Guelaguetza festival showcase millennia of continuous culture."
        ),
        image_url="https://images.unsplash.com/photo-1518638150340-f706e86654de?auto=format&fit=crop&w=1200&q=80",
        lat=17.0732,
        lng=-96.7266,
        tags=["food", "mezcal", "indigenous-culture", "festivals", "textiles"],
    ),
    dict(
        id="hoi-an",
        name="Hoi An",
        country="Vietnam",
        region="Asia",
        description=(
            "A beautifully preserved trading port on Vietnam's central coast, Hoi An's Ancient Town "
            "blends Vietnamese, Chinese, and Japanese influences in its wooden-fronted shophouses and "
            "the iconic Japanese Covered Bridge. Silk lanterns light the riverside each evening, and the "
            "surrounding countryside is known for tailoring workshops, lantern-making, and fishing villages."
        ),
        image_url="https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=1200&q=80",
        lat=15.8801,
        lng=108.3380,
        tags=["lanterns", "tailoring", "riverside", "food", "unesco"],
    ),
    dict(
        id="cusco",
        name="Cusco",
        country="Peru",
        region="South America",
        description=(
            "Once the capital of the Inca Empire, Cusco sits high in the Peruvian Andes at over 3,400 "
            "meters, its colonial churches built directly atop precise Inca stonework. It is the gateway "
            "to Machu Picchu and the Sacred Valley, and remains a living center of Quechua language, "
            "weaving traditions, and Andean cuisine."
        ),
        image_url="https://images.unsplash.com/photo-1531065208531-4036c0dba3ca?auto=format&fit=crop&w=1200&q=80",
        lat=-13.5320,
        lng=-71.9675,
        tags=["inca-history", "andes", "textiles", "hiking", "unesco"],
    ),
    dict(
        id="fez",
        name="Fez",
        country="Morocco",
        region="Africa",
        description=(
            "Morocco's spiritual and intellectual heart, Fez is home to the University of al-Qarawiyyin, "
            "founded in 859 CE and recognized as one of the oldest continuously operating universities in "
            "the world. Its medina, Fes el-Bali, is a car-free labyrinth of over 9,000 alleys, tanneries, "
            "and artisan workshops producing leather, ceramics, and brass."
        ),
        image_url="https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        lat=34.0181,
        lng=-5.0078,
        tags=["medina", "tanneries", "crafts", "history", "religious-heritage"],
    ),
    dict(
        id="luang-prabang",
        name="Luang Prabang",
        country="Laos",
        region="Asia",
        description=(
            "A former royal capital cradled by the Mekong and Nam Khan rivers, Luang Prabang is renowned "
            "for its saffron-robed monks collecting alms at dawn, gilded temple roofs, and a fusion of "
            "Lao and French colonial architecture preserved as a UNESCO World Heritage site. The nearby "
            "turquoise pools of Kuang Si and the night market's textile stalls round out its quiet pace."
        ),
        image_url="https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=1200&q=80",
        lat=19.8845,
        lng=102.1348,
        tags=["monks", "temples", "mekong", "unesco", "slow-travel"],
    ),
]


def seed_destinations(db: Client) -> None:
    collection = db.collection("destinations")
    if next(collection.limit(1).stream(), None) is not None:
        return

    for data in DESTINATIONS:
        doc_id = data["id"]
        payload = {k: v for k, v in data.items() if k != "id"}
        collection.document(doc_id).set(payload)
