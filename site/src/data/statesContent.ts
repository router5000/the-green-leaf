// Long-form, hedged context for each /states/[slug] page.
// Reviewed against state regulator sites, statutes, MPP, NCSL, and NORML.
// General information only, not legal advice.

export interface StateContent {
  overview: string
  recentChanges?: string
}

export const STATES_LAST_REVIEWED = 'October 2026'

export const statesContent: Record<string, StateContent> = {
  alabama: {
    overview:
      'Alabama has a tightly limited medical cannabis program created by the Darren Wesley "Ato" Hall Compassion Act and run by the Alabama Medical Cannabis Commission (AMCC). Patients need a qualifying condition, a recommendation from a registered physician, and a state medical cannabis card. The law does not allow smoking, vaping, or raw flower. Products are limited to forms such as tablets, capsules, tinctures, gummies, oils, and topicals. Possessing cannabis without a card is still a criminal offense, and adult-use cannabis is not legal.',
    recentChanges:
      'After years of licensing litigation, the first dispensaries began opening: one in Montgomery in June 2026, then locations in Talladega and Athens. Many other licenses are still stayed or contested, so access varies a lot by region. Check the AMCC for the current list of open dispensaries.',
  },
  alaska: {
    overview:
      'Alaska legalized adult-use cannabis by ballot measure in 2014. Adults 21 and older may possess up to one ounce and grow a small number of plants at home. Licensed retail stores are regulated by the Alcohol and Marijuana Control Office (AMCO) and the Marijuana Control Board. Alaska was one of the first states to allow on-site consumption endorsements for some retailers, but use in public places remains prohibited. Local governments can opt out of commercial licensing, so retail access differs between communities.',
  },
  arizona: {
    overview:
      'Arizona voters approved adult-use cannabis through Proposition 207 (the Smart and Safe Arizona Act) in 2020, on top of the medical program the state has run since 2010. Adults 21+ may possess up to one ounce of cannabis, of which no more than five grams may be concentrate, and may grow a limited number of plants in an enclosed, locked area out of public view. The Arizona Department of Health Services licenses dispensaries and keeps running the medical program, which has its own possession allowance for cardholders.',
  },
  arkansas: {
    overview:
      'Arkansas has a medical marijuana program created by voter-approved Amendment 98 in 2016. Registered patients may buy up to 2.5 ounces from licensed dispensaries every 14 days. A 2024 ballot measure to expand the program was removed from the ballot, and adult-use cannabis remains illegal. The Department of Health issues patient cards, and the Alcoholic Beverage Control Division regulates dispensaries and cultivators. Visiting patients may be able to apply for a temporary card. Check the state program before traveling.',
  },
  california: {
    overview:
      'California was the first state to legalize medical cannabis (1996) and has allowed adult-use cannabis since Proposition 64 in 2016. Adults 21+ may possess up to 28.5 grams (about one ounce) of flower and 8 grams of concentrate and may grow up to six plants per residence. The Department of Cannabis Control licenses businesses. Cities and counties can ban or limit storefronts, so retail access varies widely across the state, and many cities still have no licensed shops.',
  },
  colorado: {
    overview:
      'Colorado legalized adult-use cannabis through Amendment 64 in 2012 and opened some of the nation\'s first retail stores in 2014. Adults 21+ may possess and buy up to two ounces. Home grow is allowed within plant limits per person and per residence. The Marijuana Enforcement Division regulates licensed businesses, and some municipalities license hospitality and consumption businesses. Local governments may still prohibit retail sales.',
  },
  connecticut: {
    overview:
      'Connecticut legalized adult-use cannabis in 2021, and retail sales began in January 2023. Adults 21+ may possess up to 1.5 ounces on their person and up to 5 ounces secured at home or in a locked vehicle trunk or glove box. Home cultivation is allowed within per-adult and per-household plant caps. The Department of Consumer Protection regulates the adult-use and medical markets. Some towns prohibit cannabis businesses.',
  },
  delaware: {
    overview:
      'Delaware legalized adult-use possession in 2023, and licensed adult-use sales began in 2025 under the Office of the Marijuana Commissioner. Adults 21+ may possess up to one ounce of flower, along with smaller amounts of concentrate and edibles. Home cultivation is not permitted for adult-use consumers. Delaware is one of a few adult-use states with a home-grow ban. The state\'s long-running medical program continues alongside the adult-use market.',
  },
  florida: {
    overview:
      'Florida allows medical marijuana under a 2016 constitutional amendment. Patients need a qualifying condition, a certification from a qualified physician, and a registry ID card. Smokable flower is permitted for registered patients and capped at 2.5 ounces per 35-day supply. Other routes are limited by physician-certified supply. Adult-use cannabis remains illegal. A 2024 legalization amendment won majority support but fell short of the 60% required, and a 2026 initiative did not make the ballot.',
  },
  georgia: {
    overview:
      'Georgia has historically run one of the most restrictive medical programs in the country, limited to low-THC oil for registered patients. Registration goes through the Department of Public Health, and licensed production and dispensing are overseen by the Georgia Access to Medical Cannabis Commission. Possession of marijuana outside the registry remains a crime, and some cities have reduced local penalties. Adult-use cannabis is not legal.',
    recentChanges:
      'SB 220 was signed in May 2026 and took effect July 1, 2026. It removed the old 5% THC cap, set a possession limit of 12 grams of THC in labeled products, and allowed patients 21+ to vaporize. Smoking is still illegal, and vaping in public is prohibited. The Department of Public Health has until January 1, 2027 to issue implementing rules, so some details may still change.',
  },
  hawaii: {
    overview:
      'Hawaii has a medical cannabis program, not legal adult use. Registered patients may possess up to four ounces of usable cannabis, may grow up to ten plants with their caregiver, and may buy from licensed dispensaries within 15-day and 30-day purchase limits. The Department of Health runs the patient registry and dispensary licensing. For people without a card, possessing three grams or less is a civil violation with a $130 fine, which is decriminalization, not legalization. Legalization bills have been introduced but not enacted.',
    recentChanges:
      'Earlier versions of this page wrongly listed Hawaii as recreational. Adult-use cannabis is not legal in Hawaii, and the state remains medical-only.',
  },
  idaho: {
    overview:
      'Idaho has some of the strictest cannabis laws in the country. It has no medical program, no adult-use program, and no decriminalization. Possession of any amount of marijuana is a misdemeanor, and larger amounts can bring felony charges. Hemp products are subject to strict state THC rules. Bordering states such as Washington, Oregon, Nevada, and Montana have legal markets, and bringing their products into Idaho is illegal.',
    recentChanges:
      'Voters will decide HJR 4 on the November 3, 2026 ballot. It would amend the state constitution to give the Legislature sole authority to legalize marijuana and other covered substances, which would remove citizen initiatives as a route. A 2026 medical-cannabis initiative did not qualify.',
  },
  illinois: {
    overview:
      'Illinois legalized adult-use cannabis through the Cannabis Regulation and Tax Act, and sales began in 2020. Illinois residents 21+ may possess up to 30 grams of flower, 5 grams of concentrate, and 500 mg of THC in infused products. Non-residents may possess half those amounts. Home grow is generally limited to registered medical patients. Licensing is shared among several agencies, including the Department of Financial and Professional Regulation and the Department of Agriculture.',
  },
  indiana: {
    overview:
      'Indiana has no medical or adult-use cannabis program. Possessing less than 30 grams of marijuana is a Class B misdemeanor, and prior convictions or larger amounts raise the charge. CBD products made from hemp are legal under state law with labeling requirements. Indiana borders Illinois, Michigan, and Ohio, which all have legal markets, but bringing cannabis bought there into Indiana is illegal. Medical cannabis bills are introduced regularly but have not passed.',
  },
  iowa: {
    overview:
      'Iowa runs a limited Medical Cannabidiol Program, administered by Iowa HHS, rather than a full medical marijuana program. Registered patients with qualifying conditions may buy products such as capsules, tinctures, and vaporizable forms from licensed dispensaries, subject to a 4.5-gram THC limit per 90 days unless a provider certifies otherwise under program rules. Smokable flower is not allowed. Possession outside the program remains criminal.',
  },
  kansas: {
    overview:
      'Kansas has no medical or adult-use cannabis program. Possession is a misdemeanor for a first offense, and penalties increase for repeat offenses or larger quantities. Hemp-derived CBD is legal within state THC rules. Kansas borders Colorado, Missouri, and Oklahoma, which all have legal programs, and bringing cannabis across the border remains illegal. Medical marijuana bills have advanced in some sessions but have not become law.',
  },
  kentucky: {
    overview:
      'Kentucky\'s medical cannabis program, created by SB 47, began serving patients in 2025 and is run by the Kentucky Medical Cannabis Program within the Cabinet for Health and Family Services. Patients need a qualifying condition and a written certification. They may keep up to a 30-day supply at home and carry up to a 10-day supply. Raw plant material may be used for vaporizing, but smoking is prohibited. As of October 2026, the state reported more than two dozen dispensaries open across all of its licensing regions.',
  },
  louisiana: {
    overview:
      'Louisiana has a medical marijuana program, now regulated by the Louisiana Department of Health. Physicians may recommend cannabis for any condition they judge debilitating, and patients have been allowed to buy raw flower for inhalation since 2022. Products are sold through licensed pharmacies. For people without a recommendation, possessing 14 grams or less is punishable by a fine of up to $100 with no jail time. Adult-use cannabis is not legal.',
    recentChanges:
      'Act 305 (HB 568) took effect August 1, 2026. It increases penalties when marijuana possession occurs on school property, within 2,000 feet of a school, or on a school bus: up to one year and a fine of up to $1,000. The statewide penalty for 14 grams or less elsewhere did not change.',
  },
  maine: {
    overview:
      'Maine voters legalized adult-use cannabis in 2016, and licensed retail sales began in 2020. Adults 21+ may possess up to 2.5 ounces and grow plants at home within mature, immature, and seedling limits. The Office of Cannabis Policy regulates both the adult-use and medical programs. Maine\'s medical program is known for its large network of small caregivers. Municipalities must opt in before adult-use businesses can operate locally.',
  },
  maryland: {
    overview:
      'Maryland voters approved adult-use cannabis in 2022, and licensed sales began in July 2023. Adults 21+ may possess up to 1.5 ounces of flower, 12 grams of concentrate, and 750 mg of THC in edibles. Possessing more than those amounts, up to 2.5 ounces, is a civil offense. Adults may grow up to two plants per household, regardless of how many adults live there. The Maryland Cannabis Administration regulates the adult-use and medical markets.',
  },
  massachusetts: {
    overview:
      'Massachusetts legalized adult-use cannabis by ballot in 2016, and sales began in 2018. Adults 21+ may carry up to one ounce in public, keep up to ten ounces at home, and grow up to six plants per person, with a cap of 12 per household. The Cannabis Control Commission licenses retailers and runs the medical program. Local communities may limit or ban retail businesses.',
    recentChanges:
      'Question 8 is on the November 3, 2026 ballot. It would repeal legal adult-use retail sales starting January 1, 2028, keep medical marijuana, and change possession penalties. If it fails, current law stays in place. Check the Secretary of the Commonwealth for official ballot information.',
  },
  michigan: {
    overview:
      'Michigan voters legalized adult-use cannabis in 2018, and the state now has one of the largest retail markets in the country. Adults 21+ may possess up to 2.5 ounces in public (no more than 15 grams of it as concentrate), keep up to ten ounces at home, and grow up to 12 plants per household. The Cannabis Regulatory Agency licenses businesses. Many municipalities have opted out of allowing retail, so availability varies.',
  },
  minnesota: {
    overview:
      'Minnesota legalized adult-use cannabis in 2023, and possession and home grow became legal that August. Licensed retail sales began statewide in September 2025 under the Office of Cannabis Management. Adults 21+ may possess up to two ounces of flower in public and up to two pounds at home, and may grow up to eight plants per household, with no more than four mature. The state also regulates hemp-derived THC edibles and beverages.',
    recentChanges:
      'SF 4401, the 2026 omnibus bill, changes parts of the licensing and supply chain starting January 1, 2027. Hundreds of retail licenses have been issued, but not every licensed location is open yet.',
  },
  mississippi: {
    overview:
      'Mississippi\'s Medical Cannabis Act took effect in 2022, after the state Supreme Court struck down a voter-approved initiative. The Mississippi Department of Health runs the patient program, and the Department of Revenue licenses dispensaries. Purchase limits are measured in Medical Cannabis Equivalency Units (MMCEUs). Smoking is allowed for patients on private property. Possessing small amounts without a card is a low-level offense, but adult-use cannabis is not legal.',
  },
  missouri: {
    overview:
      'Missouri voters approved Amendment 3 in 2022, adding adult-use legalization to the state constitution, and retail sales began in February 2023. Adults 21+ may possess up to three ounces. Adults who get a personal cultivation registration card from the state may grow plants at home within limits. The Division of Cannabis Regulation oversees both the adult-use and medical programs. The amendment also included a process to expunge some past marijuana offenses.',
  },
  montana: {
    overview:
      'Montana voters legalized adult-use cannabis through I-190 in 2020, and retail sales began in 2022. Adults 21+ may possess up to one ounce. Home grow is limited to two mature plants and two seedlings per adult, with a cap of four of each per residence. The Cannabis Control Division of the Department of Revenue regulates licensees. Counties that voted against I-190 do not allow storefronts unless local voters approve them.',
  },
  nebraska: {
    overview:
      'In November 2024, Nebraska voters approved two medical cannabis initiatives with about 70% support. Initiative 437 protects patients who have a written recommendation from a health care practitioner and lets them possess up to five ounces. Initiative 438 created the Nebraska Medical Cannabis Commission to regulate the program. Possessing an ounce or less without that protection remains an infraction with a fine. Adult-use cannabis is not legal.',
    recentChanges:
      'The Commission adopted permanent regulations in mid-2026 and has licensed several cultivators. As of October 2026, however, no dispensaries are licensed, and patients cannot yet buy products in the state. The current rules limit products to forms like pills, tinctures, and topicals, exclude flower, smoking, vaping, and edibles, and cap THC per 90 days. Further rule amendments are expected. The Nebraska Supreme Court dismissed a challenge to the initiatives, and the Legislature passed LB 1235 on Commission fees and administration.',
  },
  nevada: {
    overview:
      'Nevada legalized adult-use cannabis in 2016. Under SB 277, which took effect January 1, 2024, adults 21+ may possess up to 2.5 ounces of usable cannabis or one-quarter ounce of concentrate. Home cultivation is allowed only for people who live more than 25 miles from a licensed store. The Cannabis Compliance Board regulates the industry and has begun licensing consumption lounges. Using cannabis in casinos, on the Las Vegas Strip, or anywhere in public is prohibited.',
  },
  'new-hampshire': {
    overview:
      'New Hampshire is the only New England state without legal adult-use cannabis. It has a Therapeutic Cannabis Program run by the Department of Health and Human Services, with patients served by licensed alternative treatment centers. For people without a card, possessing three-quarters of an ounce or less is decriminalized and punished with a civil fine. Home grow is not allowed. Adult-use legalization bills have repeatedly passed the House and failed in the Senate.',
    recentChanges:
      'In 2026 the Senate again tabled adult-use legalization bills, and the governor has said she opposes legalization. Since 2025, an open-container-style law sets a fine for using cannabis in public, though it does not apply to therapeutic use under the program.',
  },
  'new-jersey': {
    overview:
      'New Jersey voters approved adult-use cannabis in 2020, and retail sales began in April 2022. Adults 21+ may possess up to six ounces. Home cultivation is not allowed for adult-use or medical consumers, making New Jersey one of a few adult-use states with a home-grow ban. The Cannabis Regulatory Commission licenses retailers and consumption areas and runs the medical program. Municipalities may opt out of hosting cannabis businesses.',
  },
  'new-mexico': {
    overview:
      'New Mexico legalized adult-use cannabis through the Cannabis Regulation Act, and sales began in April 2022. Adults 21+ may possess up to two ounces of flower, 16 grams of extract, and 800 mg of infused edibles. Home grow is allowed up to six mature plants per person, with a household cap of 12 mature plants. The Cannabis Control Division of the Regulation and Licensing Department oversees businesses and the medical program.',
  },
  'new-york': {
    overview:
      'New York legalized adult-use cannabis through the Marihuana Regulation and Taxation Act in 2021. Adults 21+ may possess up to three ounces of flower and 24 grams of concentrate. Adults may grow up to six plants each, with a cap of 12 per household. The Office of Cannabis Management licenses dispensaries, and enforcement against unlicensed shops has grown since 2024. Cannabis may generally be smoked where tobacco smoking is allowed, with exceptions such as vehicles and many workplaces.',
  },
  'north-carolina': {
    overview:
      'North Carolina has no medical or adult-use cannabis program under state law. Possessing up to half an ounce is a Class 3 misdemeanor, the lowest criminal level, usually punished by a fine of up to $200. Larger amounts bring more serious misdemeanor or felony charges. The Eastern Band of Cherokee Indians operates its own cannabis program on tribal land in western North Carolina under tribal law, but those protections do not extend off tribal land. Medical bills have passed the state Senate in past sessions but not the House.',
    recentChanges:
      'An earlier version of this page described small-amount possession as a civil infraction. Under North Carolina law it is a Class 3 misdemeanor, which is still a criminal charge.',
  },
  'north-dakota': {
    overview:
      'North Dakota voters approved medical marijuana in 2016. Registered patients may buy up to three ounces of dried leaves or flowers in a 30-day period, along with other product limits. The program is run by the North Dakota Department of Health and Human Services. Adult-use legalization measures failed at the ballot in 2018, 2022, and 2024, so recreational cannabis remains illegal. Possessing small amounts without a card is a misdemeanor.',
  },
  ohio: {
    overview:
      'Ohio voters approved adult-use cannabis through Issue 2 in November 2023, and licensed adult-use sales began in August 2024. Adults 21+ may possess up to 2.5 ounces of plant material and 15 grams of extract, counting both homegrown and purchased cannabis. Home grow is allowed up to six plants per adult, with a cap of 12 per residence, kept secure and out of public view. The Division of Cannabis Control regulates the adult-use and medical markets.',
    recentChanges:
      'SB 56 took effect March 20, 2026 and revised the voter-approved law. It kept the 2.5-ounce and 15-gram possession limits and the home-grow caps. It added restrictions on growing in certain residences, such as childcare facilities, and where a lease prohibits it. It also prohibits smoking, combustion, and vaping in public outside qualifying private property. Hemp-derived intoxicating products face separate state and federal changes.',
  },
  oklahoma: {
    overview:
      'Oklahoma has one of the country\'s most open medical marijuana programs, created by State Question 788 in 2018 and regulated by the Oklahoma Medical Marijuana Authority (OMMA). There is no fixed list of qualifying conditions, and licensed patients may possess three ounces on their person and eight ounces at home and grow six mature and six seedling plants. Voters rejected adult-use legalization through State Question 820 in 2023. The state has since tightened licensing for businesses.',
  },
  oregon: {
    overview:
      'Oregon legalized adult-use cannabis through Measure 91 in 2014. Adults 21+ may possess up to one ounce in public and up to eight ounces of usable cannabis at home, and may grow up to four plants per household. The Oregon Liquor and Cannabis Commission regulates retailers. Oregon briefly decriminalized possession of all drugs under Measure 110, but in 2024 the Legislature restored criminal penalties for hard drugs. Legal adult-use cannabis was not affected.',
  },
  pennsylvania: {
    overview:
      'Pennsylvania has had a medical marijuana program since 2016, run by the Department of Health. Certified patients may buy up to a 30-day supply, including dry leaf for vaporization. Smoking is not permitted under program rules. Home cultivation is not allowed. Adult-use cannabis remains illegal statewide, but several cities, including Philadelphia and Pittsburgh, have reduced local penalties for small amounts.',
    recentChanges:
      'Adult-use legalization stalled again in 2026. Bills such as SB 120 did not advance out of committee, and the state budget enacted in July 2026 did not include legalization.',
  },
  'rhode-island': {
    overview:
      'Rhode Island legalized adult-use cannabis through the Cannabis Act in 2022, and retail sales began that December. Adults 21+ may possess up to one ounce in public and up to ten ounces at home, and may grow a limited number of plants. The state set up the Cannabis Control Commission to take over regulation of the adult-use and medical markets from the Department of Business Regulation. Some municipalities have opted out of retail sales.',
  },
  'south-carolina': {
    overview:
      'South Carolina has no medical marijuana program in practice and no adult-use program. A narrow law allows patients with severe epilepsy to possess certain low-THC CBD oil. Possessing an ounce or less of marijuana is a misdemeanor for a first offense, and penalties increase sharply for repeat offenses. The Compassionate Care Act, a full medical program, has passed the Senate in past sessions but not the House.',
    recentChanges:
      'The Marijuana Policy Project has noted that a little-known 1980 South Carolina law on therapeutic research could in theory support a medical program. That remains a policy argument, not an operating program.',
  },
  'south-dakota': {
    overview:
      'South Dakota voters approved medical cannabis through Initiated Measure 26 in 2020, and the program is run by the Department of Health. Registered patients may possess up to three ounces of cannabis. Some may be authorized to grow plants at home if their certification allows it. Voters approved adult-use legalization in 2020, but the state Supreme Court struck it down. Later legalization measures failed in 2022 and 2024.',
  },
  tennessee: {
    overview:
      'Tennessee has no medical or adult-use cannabis program. Possessing up to half an ounce is a Class A misdemeanor punishable by up to a year in jail. A narrow law lets certain patients possess low-THC cannabis oil obtained legally elsewhere. Hemp-derived products are sold under state rules that the Legislature has tightened in recent sessions. Federal changes to the definition of hemp may further restrict intoxicating hemp products.',
  },
  texas: {
    overview:
      'Texas does not have a full medical marijuana program. Its Compassionate Use Program (TCUP), regulated by the Department of Public Safety, lets registered patients with qualifying conditions buy low-THC cannabis prescribed by registered physicians. Possessing two ounces or less of marijuana outside the program is a Class B misdemeanor. Some cities have approved local decriminalization ordinances, which the state has challenged in court. Adult-use cannabis is illegal.',
    recentChanges:
      'HB 46 expanded TCUP. It added qualifying conditions, allowed approved non-smoked inhalation, replaced the old 1% THC-by-weight cap with a limit of 10 mg THC per dose and 1 gram per package, and authorized up to 15 dispensing organizations. In 2026 DPS conditionally selected new licensees, which may not operate until approved. State rules also limit consumable hemp products, and smokable hemp is effectively banned.',
  },
  utah: {
    overview:
      'Utah has a medical cannabis program created by the Legislature in 2018 as a compromise after voters approved Proposition 2. The Department of Health and Human Services runs patient cards, and licensed medical cannabis pharmacies sell products. Patients may buy up to a 30-day supply (113 grams of unprocessed flower or an equivalent amount of THC in other forms). Unprocessed flower must be sold in blister packs, and smoking is prohibited. Adult-use cannabis is illegal.',
  },
  vermont: {
    overview:
      'Vermont legalized adult-use possession and home grow in 2018, and licensed retail sales began in October 2022 under the Cannabis Control Board. Adults 21+ may possess up to one ounce of flower and five grams of hash, and may grow up to two mature and four immature plants per household. Towns must opt in before retail stores can open. Vermont also has a medical program regulated by the same board.',
  },
  virginia: {
    overview:
      'Virginia legalized adult-use possession and home grow on July 1, 2021, but has not yet had a legal adult-use retail market. Adults 21+ may possess up to one ounce and grow up to four plants per household, kept out of public view and labeled. Licensed medical dispensaries serve registered patients. Consuming cannabis in public carries a civil penalty, and sharing cannabis with another adult is allowed only without payment.',
    recentChanges:
      'Virginia\'s budget, signed in June 2026, authorizes adult-use retail sales starting July 1, 2027, regulated by the Virginia Cannabis Control Authority. License applications are expected to open in early 2027. The budget also raises the public possession limit to two ounces and increases the public-consumption fine. Check the Authority for exact effective dates before relying on the new limits.',
  },
  washington: {
    overview:
      'Washington legalized adult-use cannabis through Initiative 502 in 2012, alongside Colorado. Adults 21+ may possess up to one ounce of usable cannabis, 7 grams of concentrate, 16 ounces of solid infused product, and 72 ounces of liquid infused product. Home grow is not permitted for adult-use consumers. Authorized medical patients may grow a limited number of plants. The Liquor and Cannabis Board regulates the industry.',
  },
  'west-virginia': {
    overview:
      'West Virginia has a medical cannabis program created in 2017 and run by the Office of Medical Cannabis. Certified patients may buy up to a 30-day supply. Smoking is prohibited, but dry leaf or flower may be used in vaporization and other approved forms. Home cultivation is not allowed. Adult-use cannabis is illegal, and possessing marijuana without a card remains a criminal offense.',
  },
  wisconsin: {
    overview:
      'Wisconsin has no medical or adult-use cannabis program, though it allows CBD oil and hemp products. Possession is a misdemeanor for a first offense, and a second offense can be charged as a felony. Several cities, including Milwaukee and Madison, have reduced or eliminated local fines for small amounts, but state law and state penalties still apply. Wisconsin borders Illinois, Michigan, and Minnesota, which all have legal adult-use markets.',
  },
  wyoming: {
    overview:
      'Wyoming has no medical or adult-use cannabis program. Possessing three ounces or less of marijuana is a misdemeanor, and larger amounts can be charged as felonies. The state permits hemp and CBD products that meet state and federal THC limits. Wyoming borders Colorado and Montana, which both have legal markets, and bringing cannabis bought there into Wyoming is illegal. Ballot initiatives on medical cannabis and decriminalization have been attempted but have not qualified.',
  },
}

export function getStateContent(slug: string): StateContent | undefined {
  return statesContent[slug]
}
