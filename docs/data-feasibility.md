# Data Feasibility Audit — CityPulse

Date: 3 September 2026
Method: Overpass Turbo, count queries per city per category
Cities: Berlin, Munich, Lisbon
Categories: cafe, restaurant, museum, gallery, park (Berlin only)

## Coverage

| |	Cafés	|Restaurants|	Museums|	Galleries|
|---|---|---|---|---|
|Berlin — total	|2,605	|4,761|	247|	361|
|hours|	68%	|77%	|83%	|44%|
|images	|0.4%	|0.4%	|58%	|4%|
|Munich — total	|843	|2,114	|72|	170|
|hours	|82%	|86%	|92%	|75%|
|images	|0.6%	|1.9%	|69%	|5%|
|Lisbon — total	|1,158	|2,730	|103|	58|
|hours	|32%	|33%	|67%	|19%|
|images	|0.7%	|0.7%	|64%	|10%|

## Findings

1. Opening hours — Opening-hours data looks reasonably good for Berlin and Munich. Restaurants, museums, and cafés have the best coverage, with Munich generally performing better than Berlin.
Lisbon is the main exception. Only around one-third of cafés and restaurants have opening hours available. This means we cannot assume that a place is closed just because its opening hours are missing. CityPulse needs to show these places as having unknown hours instead.

2. Parks —  this needs to be handled differently from the other categories. They usually don't work like businesses where opening and closing times are essential.
For example, a park having no opening-hours information does not necessarily mean that users cannot visit it. So parks should have their own hours policy rather than using the same logic as cafés, restaurants, or museums.

3. Images — Images are the biggest weakness in the current OSM data for cafés and restaurants. In all three cities, less than 2% of these places have images.
Museums are very different, roughly 58–69% have a Wikidata link, which is our route to a freely licensed photo.. This tells us that OSM can provide useful images for some categories, but not consistently across all places.
Because of this, images should be treated as optional data. A place should still appear in CityPulse even if no image is available.

4. Galleries — Galleries have different coverage from museums, especially when it comes to images. Berlin has 44% opening-hours coverage but only 4% image coverage, while Lisbon has even lower coverage for both.
It makes more sense to keep galleries as their own category instead of putting them under museums. This also gives us the option to handle galleries differently or add another data source for them later.

5. City variation — The results show that data quality changes quite a lot from one city to another.
Berlin and Munich have relatively good opening-hours coverage, while Lisbon is much weaker for cafés and restaurants. So we shouldn't build CityPulse around the assumption that every city will have the same level of data completeness.
This is why having a city tier will be useful. It gives us a way to adjust the experience depending on how reliable the data is in each city.

## Decisions

- categories needs a default_hours_policy column because opening hours don't work the same way for every category. A restaurant needs opening hours, while a park may not.
- places needs a hours_policy column because individual places may need to behave differently from the default category rule. It also helps us distinguish between a place with known hours, a place with unknown hours, and a place where normal opening hours don't really apply.
- cities needs a tier column because the quality of the available data varies between cities. This lets us decide which features and defaults make sense for each city.
- Galleries should remain separate from museums because their data coverage is different, particularly for images. Keeping them separate will also make it easier to add category-specific rules later.
- For core-tier cities, the unknown-hours toggle should be on by default. Even in Berlin, which has relatively good coverage, a considerable number of cafés and restaurants don't have opening-hours data. If we hide those places, users would lose access to a large part of the available data.

## Open questions

- Munich counts are smaller than expected — did the geocoder resolve to the city or a smaller boundary? 

- Recommender evaluation dataset: Foursquare NYC & Tokyo check-ins
  Source: https://sites.google.com/site/yangdingqi/home/foursquare-dataset
  Terms: free to use, citation of the associated paper required
  Verified: 3 Sep 2026
  Fallback: 4TU.ResearchData mirror (DOI 10.4121/15112308), or Yelp Open Dataset
  Note: separate from OSM data. Used offline to validate the ranking
  approach only — venue IDs do not map to OSM places.
