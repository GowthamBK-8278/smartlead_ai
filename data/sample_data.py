# -----------------------------------------------------------------------------
# SmartLead AI – Sample Data Engine
# Realistic simulated lead data across 11 domains and 5 platforms.
# Each row represents a public post/comment that signals buying/enrollment intent.
# -----------------------------------------------------------------------------

import pandas as pd
import random
from datetime import datetime, timedelta


def _random_date(days_back: int = 90) -> str:
    """Generate a random ISO date string within the last N days."""
    delta = random.randint(0, days_back)
    date = datetime.now() - timedelta(days=delta)
    return date.strftime("%Y-%m-%d")


_RAW_DATA = {

    "Aviation": [
        ["YouTube",   "Pilot Training Course 2025",     "aviation_dreamer_01",  "I want to become a pilot after school, need details about admission"],
        ["YouTube",   "How to Become a Commercial Pilot","sky_chaser_007",       "What are the fees for commercial pilot license training?"],
        ["Instagram", "Flight School – Join Now",        "future_pilot_2026",    "Need aviation course details, very interested in enrolling"],
        ["Instagram", "Pilot Life Vlogs",                "cockpit_dreams",       "How long does pilot training take? Want to apply"],
        ["Facebook",  "Aviation Academy Official",       "pilot_career_goal",    "Interested in CPL training, please share admission process"],
        ["Facebook",  "Become a Pilot – Free Webinar",  "blue_sky_ankit",       "How much are the fees? Need details urgently"],
        ["Reddit",    "r/aviationCareer",               "throwaway_pilotdream", "Considering aviation as a career, which flight school should I join?"],
        ["Reddit",    "r/flying",                       "cessna_learner",       "Is instrument rating necessary before CPL? Trying to plan my course"],
        ["Twitter",   "ATC Training India",             "atc_aspirant_raj",     "Looking for Air Traffic Control training programs, how to enroll?"],
        ["Twitter",   "Pilot Ground School",            "wings_2026",           "Just finished 12th grade, want to become a pilot. Which academy to choose?"],
        ["YouTube",   "Aviation Q&A Live",              "quiz_pilot_2025",      "Great video! Can someone share the contact for admission?"],
        ["Instagram", "DGCA Exam Preparation",          "dgca_prep_star",       "Need DGCA preparation course details and fees"],
        ["Facebook",  "Helicopter Pilot Training",      "heli_dream_vikas",     "Interested in helicopter training, please send details"],
        ["Reddit",    "r/learnflying",                  "flightsim_to_real",    "Moving from sim to real training, need affordable flight school recommendations"],
        ["Twitter",   "Airline Pilot Career Fair",      "cadet_pilot_india",    "Which cadet pilot programs are open for applications in 2025?"],
    ],

    "Laptops": [
        ["YouTube",   "Top 10 Coding Laptops 2025",     "coding_student_01",    "Need laptop for coding and machine learning, which one should I buy?"],
        ["YouTube",   "Gaming Laptop Under 80K Review", "gamer_prateek",        "Interested in buying, what's the best deal right now?"],
        ["Instagram", "Dell XPS 15 Unboxing",           "tech_buyer_22",        "Want to buy this laptop, is the price worth it?"],
        ["Instagram", "HP Pavilion vs Lenovo IdeaPad",  "laptop_hunter_sam",    "Confused between these two, need help deciding which to purchase"],
        ["Facebook",  "Laptop Buying Guide 2025",       "first_laptop_buyer",   "Looking to buy my first laptop under 50K for college, which is best?"],
        ["Facebook",  "MacBook Air M3 Review",          "apple_fan_rohan",      "Planning to buy MacBook, what's the student discount available?"],
        ["Reddit",    "r/SuggestALaptop",               "cs_freshman_2025",     "Need a laptop for CS degree, budget is 60K, gaming + coding use case"],
        ["Reddit",    "r/laptops",                      "remote_work_setup",    "Best laptop for remote work? Battery life is most important for me"],
        ["Twitter",   "Lenovo Gaming Sale",             "game_rig_seeker",      "Is there any laptop deal going on? Looking to buy urgently"],
        ["Twitter",   "Student Laptop Offers",          "scholarship_student",  "Need affordable laptop for online studies, any recommendations?"],
        ["YouTube",   "ASUS ROG Review",                "rog_fan_krish",        "Comparing prices online, want to buy the best gaming laptop"],
        ["Instagram", "Acer Nitro 5 Launch",            "nitro_curious",        "What's the EMI option on this laptop? Interested in buying"],
        ["Facebook",  "Laptop Exchange Offer",          "upgrade_time_now",     "Looking to exchange old laptop and upgrade, what are the options?"],
        ["Reddit",    "r/buildapc",                     "laptop_or_pc_dilemma", "Should I buy a laptop or build a PC? Budget is 70K for development"],
        ["Twitter",   "Surface Pro 2025",               "productivity_mukesh",  "Is Surface Pro good for architecture students? Planning to purchase"],
    ],

    "Colleges": [
        ["YouTube",   "Top Engineering Colleges India 2025",   "future_engineer_01",  "Need details about engineering admission process and cutoff marks"],
        ["YouTube",   "MBA Admission Guide",                   "mba_aspirant_neha",   "Interested in MBA, what are the top colleges and their fee structure?"],
        ["Instagram", "College Life Vlogs",                    "college_seeker_raj",  "Shortlisting colleges, can someone guide on the admission procedure?"],
        ["Instagram", "Scholarship Opportunities India",       "scholarship_seeker",  "Need scholarship information for engineering, how to apply?"],
        ["Facebook",  "Engineering Colleges Open Day",         "jee_qualifier_2025",  "Qualified JEE with good rank, looking for best college options"],
        ["Facebook",  "Medical College Admission 2025",        "neet_aspirant_pooja", "NEET qualified, need guidance on MBBS admissions and fee details"],
        ["Reddit",    "r/indianengineeringstudents",           "confused_student_01", "Which branch is best for placement? Want to take admission in CS"],
        ["Reddit",    "r/MBA",                                "workex_mba_plan",     "Planning to do MBA after 2 years work ex, need help shortlisting colleges"],
        ["Twitter",   "College Counseling Session",           "counseling_needed",   "Looking for a college counselor to help with applications, any recommendations?"],
        ["Twitter",   "CUET Exam 2025",                       "cuet_prep_student",   "Appeared for CUET, need details about which colleges accept CUET scores"],
        ["YouTube",   "IIT vs NIT – Which is Better?",        "rank_confusion_help", "Got rank 5000 in JEE, IIT not possible, which NIT to prefer?"],
        ["Instagram", "Deemed University Admissions",         "deemed_uni_inquiry",  "Need admission details for deemed universities, is management quota available?"],
        ["Facebook",  "BBA Admission 2025",                   "bba_career_path",     "Interested in BBA program, what are the entrance exams I need to take?"],
        ["Reddit",    "r/college",                            "lateral_entry_doubt", "Can I do lateral entry in second year engineering? What are the requirements?"],
        ["Twitter",   "Distance MBA Programs",                "working_pro_mba",     "Looking for part-time or distance MBA while working, best options?"],
    ],

    "Courses": [
        ["YouTube",   "Data Science Full Course 2025",       "ds_learner_amit",     "Interested in data science course, what are the fees and duration?"],
        ["YouTube",   "Python Crash Course for Beginners",   "code_newbie_sara",    "Want to join Python training, is this good for beginners?"],
        ["Instagram", "AI & Machine Learning Bootcamp",      "ml_curious_dev",      "Need AI course details, batch starting date and enrollment process"],
        ["Instagram", "Full Stack Development Course",       "fullstack_dreamer",   "Interested in web development, looking for a job-ready program"],
        ["Facebook",  "Digital Marketing Certification",     "marketing_learner",   "Need digital marketing course fees and what certifications are provided"],
        ["Facebook",  "Data Analytics Course – Enroll Now",  "analytics_beginner",  "How much does the data analytics course cost? Is there EMI option?"],
        ["Reddit",    "r/learnpython",                       "career_switch_techie","Want to switch career to data science, which course should I join?"],
        ["Reddit",    "r/MachineLearning",                   "ml_self_study_help",  "Self studying ML, should I join a structured course or continue self-paced?"],
        ["Twitter",   "Coursera vs Udemy vs NPTEL",          "online_learner_2025", "Which platform has the best data science course? Need recommendations"],
        ["Twitter",   "AI Course for Non-Techies",           "non_tech_learner_01", "Can a non-technical person learn AI? Looking for beginner courses"],
        ["YouTube",   "Tableau Data Visualization",         "viz_curious_priya",   "Interested in learning Tableau, any good course recommendations with placement?"],
        ["Instagram", "Cloud Computing Course AWS",         "cloud_career_ankit",  "Need AWS certification course details, how long does it take to complete?"],
        ["Facebook",  "Cybersecurity Course 2025",          "security_interested", "Interested in ethical hacking course, please share syllabus and fees"],
        ["Reddit",    "r/learnprogramming",                 "java_spring_learner", "Best Java Spring Boot course for backend development? Need structured curriculum"],
        ["Twitter",   "Power BI Training Workshop",         "bi_tool_beginner",    "Looking for Power BI training, is there a weekend batch available?"],
    ],

    "Real Estate": [
        ["YouTube",   "Top Residential Projects Mumbai 2025",   "property_buyer_raj",    "Looking to buy a 2BHK flat, what's the price range in Thane?"],
        ["YouTube",   "Home Loan Guide 2025",                   "home_loan_seeker",      "Need details about home loan eligibility and EMI for 50 lakh property"],
        ["Instagram", "New Launch – Luxury Apartments",         "luxury_home_hunter",    "Interested in site visit, please share the location and contact details"],
        ["Instagram", "Ready to Move Flats – Pune",            "pune_flat_inquiry",     "Ready to move in, what's the possession date and booking amount?"],
        ["Facebook",  "Property Expo 2025",                     "invest_in_property",    "Attending property expo, looking for good investment options in realty"],
        ["Facebook",  "3BHK Villa for Sale – Hyderabad",       "villa_buyer_srinivas",  "Interested in villa purchase, is bank loan available? What's the price?"],
        ["Reddit",    "r/realestateindia",                      "first_home_buyer_01",   "First time home buyer, confused about builder vs resale. Need guidance"],
        ["Reddit",    "r/personalfinance",                      "rera_compliance_check", "How to verify if a project is RERA approved before booking?"],
        ["Twitter",   "Smart City Project Launch",              "smart_city_investor",   "Any good smart city projects for investment under 30 lakhs?"],
        ["Twitter",   "Plot for Sale – Bengaluru Outskirts",    "land_buyer_mahesh",     "Looking for plot purchase near Bangalore, what are the legal documents needed?"],
        ["YouTube",   "Rental Income Strategy India",          "passive_income_realty", "Planning to buy property for rental income, which cities are best?"],
        ["Instagram", "Commercial Office Space – Delhi NCR",   "office_space_seeker",   "Need commercial space for startup office, what are the lease terms?"],
        ["Facebook",  "Affordable Housing Scheme 2025",        "pmay_beneficiary",      "Am I eligible for PMAY scheme? How to apply for affordable housing?"],
        ["Reddit",    "r/mumbai",                              "bandra_flat_hunt",      "Looking for 1BHK in Bandra West, budget 80L, any leads?"],
        ["Twitter",   "NRI Real Estate Investment India",       "nri_property_buyer",    "NRI looking to invest in Indian real estate, which cities give best returns?"],
    ],

    "Jobs": [
        ["YouTube",   "Top IT Companies Hiring 2025",       "fresher_job_hunter",   "Looking for my first job in software development, how to apply?"],
        ["YouTube",   "Government Job Preparation Guide",   "sarkari_job_aspirant", "Preparing for government job exams, need guidance on best strategy"],
        ["Instagram", "Walk-in Interview – MNC Hiring",     "walk_in_ready_01",     "Interested in walk-in interview, what documents do I need to carry?"],
        ["Instagram", "Remote Jobs India 2025",             "wfh_job_seeker",       "Looking for remote job opportunities in data analysis, how to apply?"],
        ["Facebook",  "Job Fair – 500 Openings",            "job_fair_attendee",    "Will attend the job fair, need help with resume preparation"],
        ["Facebook",  "Management Trainee Program 2025",    "mt_program_inquiry",   "Interested in management trainee role, what's the selection process?"],
        ["Reddit",    "r/developersIndia",                  "python_job_seeker",    "2 years Python experience, looking for job switch, any referrals?"],
        ["Reddit",    "r/cscareerquestions",                "tier2_college_grad",   "Graduated from tier 2 college, how to land job in top product companies?"],
        ["Twitter",   "LinkedIn Job Alerts",                "active_job_search_01", "Actively looking for data science roles, open to relocation"],
        ["Twitter",   "Startup Hiring Announcement",        "startup_culture_fan",  "Interested in joining early-stage startup, what are the openings available?"],
        ["YouTube",   "FAANG Interview Preparation",        "faang_dream_coder",    "Targeting Amazon and Google, need interview prep roadmap"],
        ["Instagram", "HR Internship Program",              "hr_career_starter",    "Interested in HR internship, how to apply and what's the stipend?"],
        ["Facebook",  "BPO Jobs – Immediate Joining",       "bpo_job_interested",   "Need job urgently, am I eligible for BPO openings? How to apply?"],
        ["Reddit",    "r/jobs",                             "career_change_30s",    "Planning career change at 32, from marketing to data analytics, feasible?"],
        ["Twitter",   "Naukri Job Search Tips",             "job_seeker_tips_fan",  "Any tips for ATS-friendly resume? Sending many applications without response"],
    ],

    "Insurance": [
        ["YouTube",   "Best Term Insurance Plans 2025",       "term_plan_buyer",      "Want to buy term insurance, which plan has highest claim settlement ratio?"],
        ["YouTube",   "Health Insurance Explained",           "health_cover_needed",  "Looking for health insurance for family of 4, what's the best plan?"],
        ["Instagram", "LIC vs Private Insurance",             "lic_vs_hdfc_seeker",   "Confused between LIC and private insurance, need comparison and premium details"],
        ["Instagram", "ULIP vs Term Plan – Which is Better?", "investment_insurance", "Should I buy ULIP or term plan? Need expert advice on best option"],
        ["Facebook",  "Car Insurance Renewal Offers",         "car_insure_renew",     "Car insurance renewal is due, which company offers best coverage and price?"],
        ["Facebook",  "Critical Illness Cover 2025",          "critical_illness_ques","Need critical illness insurance, what conditions are covered?"],
        ["Reddit",    "r/personalfinanceindia",               "first_insurance_buy",  "26 years old, first job, should I buy term insurance now? Which plan?"],
        ["Reddit",    "r/insurance",                          "claim_process_query",  "How does insurance claim settlement work? Had a medical emergency last month"],
        ["Twitter",   "Group Health Insurance for Startups",  "startup_hr_insurance", "Setting up group health insurance for 30 employees, need quote and options"],
        ["Twitter",   "Best Travel Insurance 2025",           "frequent_traveler_01", "Traveling abroad next month, which travel insurance plan is best?"],
        ["YouTube",   "Zero Cost Term Plan Explained",        "zero_cost_plan_info",  "Interested in zero cost term plan feature, how does it work?"],
        ["Instagram", "Bike Insurance Online",                "bike_insure_online",   "Need to renew bike insurance online, which app is easiest to use?"],
        ["Facebook",  "Senior Citizen Health Insurance",      "parent_health_cover",  "Need health insurance for parents aged 65+, any affordable plans?"],
        ["Reddit",    "r/India",                              "insurance_premium_hike","Insurance premium increased significantly, should I port to another company?"],
        ["Twitter",   "Term Plan – Claim Stories",            "secure_family_future", "After watching claim success stories, I'm convinced. Need to buy term plan ASAP"],
    ],

    "Cars": [
        ["YouTube",   "Top 5 Family Cars Under 12 Lakh 2025", "family_car_buyer",     "Want to buy a car for family, 7-seater under 12 lakhs, which is best?"],
        ["YouTube",   "Electric Car India – Which to Buy?",   "ev_curious_customer",  "Planning to switch to electric car, what's the charging infrastructure like?"],
        ["Instagram", "Hyundai Creta 2025 Launch",            "suv_seeker_priya",     "Interested in test drive, please share the nearest showroom details"],
        ["Instagram", "Maruti Suzuki Grand Vitara Review",    "vitara_fan_arjun",     "On road price in Delhi? Want to book this week"],
        ["Facebook",  "Tata Nexon EV – Owner Review",        "ev_convert_willing",   "After this review, I'm ready to switch to EV. How to book the Nexon EV?"],
        ["Facebook",  "Used Car Marketplace",                 "used_car_buyer_01",    "Looking for a used car under 5 lakh, certified pre-owned preferred"],
        ["Reddit",    "r/CarsIndia",                          "first_car_buyer_guide","First time car buyer, confused between hatchback and compact SUV, budget 8L"],
        ["Reddit",    "r/electricvehicles",                   "ev_range_anxiety",     "Planning EV purchase but worried about range, which EV has best range in India?"],
        ["Twitter",   "Car Exchange Offer – Season Sale",     "exchange_my_old_car",  "Want to exchange my 2018 car for new model, what's the exchange value?"],
        ["Twitter",   "MG Motor New Launch",                  "mg_hector_interested", "Interested in MG Hector, what are the finance options available?"],
        ["YouTube",   "Kia Seltos vs Hyundai Creta 2025",    "seltos_vs_creta",      "Deciding between these two, which one should I buy for highway driving?"],
        ["Instagram", "BMW 3 Series 2025 India",             "luxury_car_aspire",    "Dream car! What's the on-road price and wait period?"],
        ["Facebook",  "Car Loan – EMI Calculator",           "car_loan_calculator",  "Planning to take car loan of 6 lakhs for 5 years, what's the EMI?"],
        ["Reddit",    "r/india",                              "petrol_vs_diesel_2025","Should I buy petrol or diesel car now with current fuel prices?"],
        ["Twitter",   "Auto Expo 2025 Highlights",           "auto_expo_visitor",    "Visited auto expo, impressed with concept cars. When are they launching?"],
    ],

    "Training Programs": [
        ["YouTube",   "Corporate Training Programs 2025",      "hr_manager_traineelook","Looking for corporate training vendor for our 50-member sales team"],
        ["YouTube",   "Leadership Skills Workshop India",      "team_lead_growth_01",  "Interested in leadership program for mid-level managers, what are the options?"],
        ["Instagram", "Soft Skills Masterclass",               "communication_improve", "Need communication skills training, is there an online option available?"],
        ["Instagram", "Sales Training Bootcamp – 3 Days",      "sales_target_achiever","Our team needs sales training, can you do an in-house workshop?"],
        ["Facebook",  "Digital Marketing Training – Live",     "dmtraining_interested","Interested in digital marketing training program, what's the ROI for businesses?"],
        ["Facebook",  "Professional Certification Programs",   "cert_program_seeker",  "Need professional certification training for finance team, what's available?"],
        ["Reddit",    "r/humanresources",                      "employee_upskilling",  "Planning employee upskilling program, which L&D vendors are best in India?"],
        ["Reddit",    "r/sales",                               "sdr_training_help",    "New to SDR role, need structured sales training program recommendation"],
        ["Twitter",   "Train the Trainer Program",             "corporate_trainer_01", "Interested in train the trainer certification, what are the prerequisites?"],
        ["Twitter",   "Six Sigma Certification Workshop",      "process_improve_seeker","Looking for Six Sigma Green Belt training, when is the next batch?"],
        ["YouTube",   "Public Speaking Training – 30 Days",   "stage_fright_overcome","I freeze on stage, this training looks perfect. How to enroll?"],
        ["Instagram", "NLP Practitioner Certification",        "nlp_curious_learner",  "Interested in NLP certification, is this valid internationally?"],
        ["Facebook",  "Time Management Workshop – Free",       "productivity_seeker",  "Registering for free workshop, is there a paid advanced program after this?"],
        ["Reddit",    "r/productivity",                        "habit_training_course","Looking for habit formation corporate training program for my company"],
        ["Twitter",   "Design Thinking Workshop",              "innovation_team_lead", "Want to conduct design thinking session for product team, who to contact?"],
    ],

    "Mobiles": [
        ["YouTube",   "Best Smartphone Under 20K 2025",       "budget_phone_buyer",   "Need a good phone under 20K for daily use and photography, which to buy?"],
        ["YouTube",   "iPhone 16 vs Samsung Galaxy S25",      "flagship_phone_seeker","Planning to upgrade to flagship, which phone is better value for money?"],
        ["Instagram", "OnePlus 13 Launch India",              "oneplus_loyal_user",   "Pre-ordering as soon as it's available! What's the launch price?"],
        ["Instagram", "Realme GT 7 Review",                   "realme_fan_vivek",     "Great camera for this price! Where can I buy at best price?"],
        ["Facebook",  "Redmi Note 14 Pro – Available Now",    "redmi_note_buyer",     "Best budget phone! What's the EMI option? Want to buy today"],
        ["Facebook",  "POCO F7 – Value Flagship",             "poco_performance_fan", "Interested in buying, is this available offline or only online?"],
        ["Reddit",    "r/Android",                             "android_phone_advice", "Moving from iOS to Android, which phone should I start with?"],
        ["Reddit",    "r/india",                               "phone_upgrade_dilemma","Using 4-year-old phone, thinking of upgrading. 5G worth paying extra for?"],
        ["Twitter",   "Apple iPhone Student Offer",           "student_apple_buyer",  "Is there student discount on iPhone? Planning to buy before college starts"],
        ["Twitter",   "Google Pixel 9a India Launch",         "pixel_camera_lover",   "Waiting for Pixel 9a India launch! What's the expected price?"],
        ["YouTube",   "5G Phones Under 15K – Best Picks",     "5g_network_ready",     "5G is available in my city now, which affordable 5G phone to buy?"],
        ["Instagram", "Samsung Galaxy A35 Camera Test",       "mid_range_cam_fan",    "Impressed with camera! Is there any exchange offer available?"],
        ["Facebook",  "Refurbished iPhone – Certified",       "refurb_phone_buyer",   "Looking for certified refurbished iPhone, where to buy safely?"],
        ["Reddit",    "r/Smartphones",                        "camera_phone_priority","Camera quality is my priority, best phone under 30K for photography?"],
        ["Twitter",   "Motorola Edge 50 Ultra Review",        "motorola_comeback_fan","Motorola making a comeback! What's the on-road price and availability?"],
    ],

    "Coding Bootcamps": [
        ["YouTube",   "Best Coding Bootcamps India 2025",     "bootcamp_researcher",  "Comparing bootcamps, need details on placement guarantee and fees"],
        ["YouTube",   "Full Stack Bootcamp Review – 6 Month", "web_dev_career_start", "Interested in joining this bootcamp, what's the admission process?"],
        ["Instagram", "Data Science Bootcamp – Enroll Now",   "ds_bootcamp_seeker",   "12-week bootcamp looks intense! Is there scholarship option available?"],
        ["Instagram", "UI/UX Design Bootcamp 2025",           "design_career_switch", "Switching from finance to design, is this bootcamp beginner-friendly?"],
        ["Facebook",  "Coding Bootcamp – Job Guarantee",      "placement_or_refund",  "Job guarantee program! What happens if I don't get placed?"],
        ["Facebook",  "DevOps Bootcamp – Weekend Batch",      "devops_weekend_batch", "Weekend batch is perfect for working professionals! How to register?"],
        ["Reddit",    "r/learnprogramming",                   "bootcamp_vs_degree",   "Is coding bootcamp worth it compared to CS degree? Career switch advice needed"],
        ["Reddit",    "r/cscareerquestions",                  "bootcamp_grad_job",    "Bootcamp graduate here, struggling to get first job. Any advice?"],
        ["Twitter",   "Upgrad Full Stack Program",            "upgrad_program_check", "Reviewing Upgrad program, is it worth the investment for placement?"],
        ["Twitter",   "Masai School – Admissions Open",       "masai_admission_2025", "Applied to Masai School, what's the selection criteria?"],
        ["YouTube",   "Zero to Hero Python Bootcamp",         "python_zero_hero",     "Perfect for beginners! Is there a live mentorship option in this course?"],
        ["Instagram", "Cybersecurity Bootcamp – Live",        "cyber_sec_interested", "Interested in cybersecurity career, is this bootcamp recognized by industry?"],
        ["Facebook",  "Cloud Computing Bootcamp – AWS/GCP",   "cloud_bootcamp_query", "Which cloud certifications will I get after completing this bootcamp?"],
        ["Reddit",    "r/india",                               "coding_bootcamp_india","Best coding bootcamp in India with good placement support? Budget is 1 lakh"],
        ["Twitter",   "Newton School – New Batch",            "newton_school_apply",  "Newton School admissions open! What's the income share agreement terms?"],
    ],
}


def get_sample_data(domain: str) -> pd.DataFrame:
    """Return a DataFrame of sample lead data for a given domain."""
    raw = _RAW_DATA.get(domain, [])
    if not raw:
        return pd.DataFrame(columns=["Platform", "Title", "Username", "Comment", "Date"])

    rows = []
    for item in raw:
        rows.append({
            "Platform": item[0],
            "Title":    item[1],
            "Username": item[2],
            "Comment":  item[3],
            "Date":     _random_date(90),
        })

    return pd.DataFrame(rows)


def get_all_domains() -> list:
    """Return sorted list of all domains with sample data."""
    return sorted(_RAW_DATA.keys())