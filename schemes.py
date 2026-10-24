SCHEMES = [

    # =========================
    # WOMEN & CHILD
    # =========================

    {
        "id": 1,
        "name": "Beti Bachao Beti Padhao",
        "category": "Women & Child",
        "description": "A government initiative focused on the education, protection and empowerment of the girl child.",
        "target_group": "Girls and women",
        "gender": "Female",
        "min_age": 0,
        "max_age": None,
        "income_limit": None,
        "student": True,
        "farmer": False,
        "benefits": "Supports awareness, education and empowerment of the girl child.",
        "documents": ["Aadhaar Card", "Birth Certificate", "Address Proof"],
        "apply_link": "https://www.myscheme.gov.in/"
    },

    {
        "id": 2,
        "name": "Pradhan Mantri Matru Vandana Yojana",
        "category": "Women & Child",
        "description": "Maternity benefit scheme providing financial support to eligible pregnant and lactating women.",
        "target_group": "Pregnant and lactating women",
        "gender": "Female",
        "min_age": 18,
        "max_age": None,
        "income_limit": 800000,
        "student": False,
        "farmer": False,
        "benefits": "Maternity-related financial assistance.",
        "documents": ["Aadhaar Card", "Bank Account", "Pregnancy/Maternity Documents"],
        "apply_link": "https://www.myscheme.gov.in/"
    },

    {
        "id": 3,
        "name": "Sukanya Samriddhi Yojana",
        "category": "Women & Child",
        "description": "Small savings scheme designed for the financial future of a girl child.",
        "target_group": "Girl child",
        "gender": "Female",
        "min_age": 0,
        "max_age": 10,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Long-term savings and interest benefits for a girl child's future.",
        "documents": ["Birth Certificate", "Guardian ID", "Address Proof"],
        "apply_link": "https://www.indiapost.gov.in/"
    },

    {
        "id": 4,
        "name": "Mission Shakti",
        "category": "Women & Child",
        "description": "Umbrella programme for the safety, security and empowerment of women.",
        "target_group": "Women",
        "gender": "Female",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Support and services for women's safety and empowerment.",
        "documents": ["Aadhaar Card", "Address Proof"],
        "apply_link": "https://missionshakti.wcd.gov.in/"
    },

    {
        "id": 5,
        "name": "POSHAN 2.0",
        "category": "Women & Child",
        "description": "Government programme addressing nutrition and development of children, pregnant women and lactating mothers.",
        "target_group": "Children, pregnant women and lactating mothers",
        "gender": "All",
        "min_age": 0,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Nutrition and health support.",
        "documents": ["Aadhaar Card", "Address Proof"],
        "apply_link": "https://www.poshantracker.in/"
    },


    # =========================
    # EDUCATION & LEARNING
    # =========================

    {
        "id": 6,
        "name": "National Scholarship Portal Schemes",
        "category": "Education & Learning",
        "description": "Online platform providing access to multiple government scholarship schemes.",
        "target_group": "Students",
        "gender": "All",
        "min_age": 5,
        "max_age": 35,
        "income_limit": 800000,
        "student": True,
        "farmer": False,
        "benefits": "Financial assistance for eligible students.",
        "documents": ["Aadhaar Card", "Income Certificate", "Marksheet", "Bank Account"],
        "apply_link": "https://scholarships.gov.in/"
    },

    {
        "id": 7,
        "name": "PM-USP Central Sector Scheme of Scholarship",
        "category": "Education & Learning",
        "description": "Scholarship support for meritorious students pursuing higher education.",
        "target_group": "College and university students",
        "gender": "All",
        "min_age": 17,
        "max_age": 25,
        "income_limit": 450000,
        "student": True,
        "farmer": False,
        "benefits": "Financial support for higher education.",
        "documents": ["Marksheet", "Income Certificate", "Aadhaar Card", "Bank Account"],
        "apply_link": "https://scholarships.gov.in/"
    },

    {
        "id": 8,
        "name": "Post-Matric Scholarship",
        "category": "Education & Learning",
        "description": "Scholarship support for eligible students studying after matriculation.",
        "target_group": "Students",
        "gender": "All",
        "min_age": 14,
        "max_age": 35,
        "income_limit": 250000,
        "student": True,
        "farmer": False,
        "benefits": "Financial assistance for post-matric education.",
        "documents": ["Caste Certificate", "Income Certificate", "Marksheet", "Aadhaar Card"],
        "apply_link": "https://scholarships.gov.in/"
    },

    {
        "id": 9,
        "name": "Pre-Matric Scholarship",
        "category": "Education & Learning",
        "description": "Scholarship assistance for eligible school students.",
        "target_group": "School students",
        "gender": "All",
        "min_age": 6,
        "max_age": 16,
        "income_limit": 250000,
        "student": True,
        "farmer": False,
        "benefits": "Financial assistance for school education.",
        "documents": ["School Certificate", "Income Certificate", "Aadhaar Card"],
        "apply_link": "https://scholarships.gov.in/"
    },

    {
        "id": 10,
        "name": "PM SHRI",
        "category": "Education & Learning",
        "description": "Government initiative supporting development of quality schools.",
        "target_group": "School students",
        "gender": "All",
        "min_age": 5,
        "max_age": 18,
        "income_limit": None,
        "student": True,
        "farmer": False,
        "benefits": "Improved educational facilities and learning environment.",
        "documents": ["Student ID", "School Records"],
        "apply_link": "https://pmshrischools.education.gov.in/"
    },


    # =========================
    # HEALTH & WELLNESS
    # =========================

    {
        "id": 11,
        "name": "Ayushman Bharat – PM-JAY",
        "category": "Health & Wellness",
        "description": "Health assurance scheme providing cashless healthcare coverage to eligible families.",
        "target_group": "Eligible families",
        "gender": "All",
        "min_age": 0,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Cashless hospitalisation and healthcare coverage.",
        "documents": ["Aadhaar Card", "Ration Card", "Eligibility Proof"],
        "apply_link": "https://nha.gov.in/PM-JAY"
    },

    {
        "id": 12,
        "name": "Ayushman Bharat Digital Mission",
        "category": "Health & Wellness",
        "description": "Digital health infrastructure initiative enabling digital health records and services.",
        "target_group": "Citizens",
        "gender": "All",
        "min_age": 0,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Access to digital health identity and health services.",
        "documents": ["Aadhaar Card", "Mobile Number"],
        "apply_link": "https://abdm.gov.in/"
    },

    {
        "id": 13,
        "name": "National Health Mission",
        "category": "Health & Wellness",
        "description": "Government health programme supporting accessible and affordable healthcare.",
        "target_group": "Citizens",
        "gender": "All",
        "min_age": 0,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Access to various public health services.",
        "documents": ["Aadhaar Card", "Health Records where applicable"],
        "apply_link": "https://www.myscheme.gov.in/schemes/nhm"
    },


    # =========================
    # AGRICULTURE & RURAL
    # =========================

    {
        "id": 14,
        "name": "PM-KISAN",
        "category": "Agriculture & Rural Development",
        "description": "Income support scheme for eligible farmer families.",
        "target_group": "Farmers",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": True,
        "benefits": "Income support to eligible farmer families.",
        "documents": ["Aadhaar Card", "Land Records", "Bank Account"],
        "apply_link": "https://pmkisan.gov.in/"
    },

    {
        "id": 15,
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "category": "Agriculture & Rural Development",
        "description": "Crop insurance scheme protecting farmers against crop losses.",
        "target_group": "Farmers",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": True,
        "benefits": "Crop insurance against specified risks and losses.",
        "documents": ["Aadhaar Card", "Land Records", "Bank Account"],
        "apply_link": "https://pmfby.gov.in/"
    },

    {
        "id": 16,
        "name": "Pradhan Mantri Krishi Sinchayee Yojana",
        "category": "Agriculture & Rural Development",
        "description": "Programme promoting irrigation development and efficient water use in agriculture.",
        "target_group": "Farmers",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": True,
        "benefits": "Support for irrigation and water-use efficiency.",
        "documents": ["Aadhaar Card", "Land Records"],
        "apply_link": "https://pmksy.gov.in/"
    },

    {
        "id": 17,
        "name": "MGNREGA",
        "category": "Agriculture & Rural Development",
        "description": "Rural employment programme providing guaranteed wage employment to rural households.",
        "target_group": "Rural households",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Wage employment opportunities in rural areas.",
        "documents": ["Aadhaar Card", "Job Card", "Address Proof"],
        "apply_link": "https://nrega.nic.in/"
    },


    # =========================
    # HOUSING & BASIC NEEDS
    # =========================

    {
        "id": 18,
        "name": "PM Awas Yojana – Gramin",
        "category": "Housing & Basic Needs",
        "description": "Housing assistance for eligible rural households.",
        "target_group": "Rural households",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Financial assistance for construction of a house.",
        "documents": ["Aadhaar Card", "Address Proof", "Bank Account"],
        "apply_link": "https://pmayg.dord.gov.in/"
    },

    {
        "id": 19,
        "name": "PM Awas Yojana – Urban",
        "category": "Housing & Basic Needs",
        "description": "Housing assistance for eligible urban households.",
        "target_group": "Urban households",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": 900000,
        "student": False,
        "farmer": False,
        "benefits": "Support for affordable housing.",
        "documents": ["Aadhaar Card", "Income Certificate", "Address Proof"],
        "apply_link": "https://pmay-urban.gov.in/"
    },

    {
        "id": 20,
        "name": "Jal Jeevan Mission",
        "category": "Housing & Basic Needs",
        "description": "Programme aimed at providing functional tap water connections to rural households.",
        "target_group": "Rural households",
        "gender": "All",
        "min_age": 0,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Access to household tap water supply.",
        "documents": ["Address Proof"],
        "apply_link": "https://jaljeevanmission.gov.in/"
    },


    # =========================
    # EMPLOYMENT & SKILLS
    # =========================

    {
        "id": 21,
        "name": "Pradhan Mantri Kaushal Vikas Yojana",
        "category": "Employment & Skills",
        "description": "Skill development programme providing training and certification opportunities.",
        "target_group": "Youth",
        "gender": "All",
        "min_age": 15,
        "max_age": 45,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Skill training and certification.",
        "documents": ["Aadhaar Card", "Education Certificate"],
        "apply_link": "https://www.skillindiadigital.gov.in/"
    },

    {
        "id": 22,
        "name": "Pradhan Mantri Mudra Yojana",
        "category": "Employment & Skills",
        "description": "Loan support for micro and small business activities.",
        "target_group": "Entrepreneurs and small businesses",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Credit support for eligible micro enterprises.",
        "documents": ["Aadhaar Card", "PAN Card", "Business Documents"],
        "apply_link": "https://www.mudra.org.in/"
    },

    {
        "id": 23,
        "name": "PM SVANidhi",
        "category": "Employment & Skills",
        "description": "Working capital support for street vendors.",
        "target_group": "Street vendors",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Working capital loan support for street vendors.",
        "documents": ["Aadhaar Card", "Street Vendor Certificate/ID", "Bank Account"],
        "apply_link": "https://pmsvanidhi.mohua.gov.in/"
    },

    {
        "id": 24,
        "name": "National Apprenticeship Promotion Scheme",
        "category": "Employment & Skills",
        "description": "Programme promoting apprenticeship training and industry skills.",
        "target_group": "Apprentices",
        "gender": "All",
        "min_age": 14,
        "max_age": 35,
        "income_limit": None,
        "student": True,
        "farmer": False,
        "benefits": "Apprenticeship and skill development opportunities.",
        "documents": ["Aadhaar Card", "Education Certificate", "Bank Account"],
        "apply_link": "https://www.apprenticeshipindia.gov.in/"
    },


    # =========================
    # SOCIAL SECURITY
    # =========================

    {
        "id": 25,
        "name": "Atal Pension Yojana",
        "category": "Social Security",
        "description": "Pension scheme designed to provide retirement income security.",
        "target_group": "Eligible citizens",
        "gender": "All",
        "min_age": 18,
        "max_age": 40,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Pension after reaching eligible age subject to scheme conditions.",
        "documents": ["Aadhaar Card", "Bank Account"],
        "apply_link": "https://www.pfrda.org.in/"
    },

    {
        "id": 26,
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
        "category": "Social Security",
        "description": "Life insurance scheme providing risk coverage to eligible subscribers.",
        "target_group": "Eligible bank account holders",
        "gender": "All",
        "min_age": 18,
        "max_age": 50,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Life insurance coverage subject to scheme terms.",
        "documents": ["Aadhaar Card", "Bank Account"],
        "apply_link": "https://jansuraksha.gov.in/"
    },

    {
        "id": 27,
        "name": "Pradhan Mantri Suraksha Bima Yojana",
        "category": "Social Security",
        "description": "Accident insurance scheme for eligible bank account holders.",
        "target_group": "Eligible bank account holders",
        "gender": "All",
        "min_age": 18,
        "max_age": 70,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Accident insurance coverage subject to scheme terms.",
        "documents": ["Aadhaar Card", "Bank Account"],
        "apply_link": "https://jansuraksha.gov.in/"
    },


    # =========================
    # BANKING & FINANCIAL INCLUSION
    # =========================

    {
        "id": 28,
        "name": "Pradhan Mantri Jan Dhan Yojana",
        "category": "Banking & Financial Inclusion",
        "description": "Financial inclusion programme providing access to basic banking services.",
        "target_group": "Citizens",
        "gender": "All",
        "min_age": 10,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Access to basic banking facilities and financial services.",
        "documents": ["Aadhaar Card", "Address Proof"],
        "apply_link": "https://www.pmjdy.gov.in/"
    },

    {
        "id": 29,
        "name": "Stand-Up India",
        "category": "Banking & Financial Inclusion",
        "description": "Bank loan support for eligible SC/ST and women entrepreneurs.",
        "target_group": "SC/ST and women entrepreneurs",
        "gender": "Female",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Bank loan support for starting eligible enterprises.",
        "documents": ["Aadhaar Card", "PAN Card", "Business Plan", "Caste Certificate where applicable"],
        "apply_link": "https://www.standupmitra.in/"
    },

    {
        "id": 30,
        "name": "National Social Assistance Programme",
        "category": "Banking & Financial Inclusion",
        "description": "Social assistance programme supporting vulnerable citizens through pensions and assistance.",
        "target_group": "Poor and vulnerable citizens",
        "gender": "All",
        "min_age": 18,
        "max_age": None,
        "income_limit": None,
        "student": False,
        "farmer": False,
        "benefits": "Social assistance under applicable pension and welfare components.",
        "documents": ["Aadhaar Card", "Income/BPL Proof", "Bank Account"],
        "apply_link": "https://nsap.dord.gov.in/"
    }
]


# =====================================================
# CATEGORY LIST
# =====================================================

CATEGORIES = [
    "All Categories",
    "Women & Child",
    "Education & Learning",
    "Health & Wellness",
    "Agriculture & Rural Development",
    "Housing & Basic Needs",
    "Employment & Skills",
    "Social Security",
    "Banking & Financial Inclusion"
]