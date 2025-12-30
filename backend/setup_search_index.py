"""
Setup Azure AI Search Index with Medical Knowledge Base
Creates index schema and populates with sample medical data
"""
import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType
)
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

def create_index():
    """Create the medical-kb search index."""
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_key = os.getenv("SEARCH_KEY")
    index_name = "medical-kb"
    
    # Create index client
    index_client = SearchIndexClient(
        endpoint=search_endpoint,
        credential=AzureKeyCredential(search_key)
    )
    
    # Define index schema
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="source", type=SearchFieldDataType.String),
    ]
    
    # Create index
    index = SearchIndex(name=index_name, fields=fields)
    
    try:
        index_client.create_index(index)
        print(f"✓ Created index: {index_name}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"✓ Index already exists: {index_name}")
        else:
            print(f"✗ Error creating index: {str(e)}")
            raise

def populate_index():
    """Populate index with medical knowledge base documents."""
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_key = os.getenv("SEARCH_KEY")
    index_name = "medical-kb"
    
    # Create search client
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(search_key)
    )
    
    # Sample medical knowledge base documents
    documents = [
        # Simple - Office Information
        {
            "id": "1",
            "title": "Office Hours and Contact Information",
            "content": "Our clinic is open Monday through Friday from 8:00 AM to 6:00 PM, and Saturday from 9:00 AM to 1:00 PM. We are closed on Sundays and major holidays. For appointments, call (555) 123-4567. For urgent matters after hours, call our 24/7 nurse hotline at (555) 123-4568. Our address is 123 Medical Plaza, Healthcare City, HC 12345.",
            "category": "administrative",
            "source": "clinic_handbook"
        },
        {
            "id": "2",
            "title": "Appointment Scheduling and Cancellation Policy",
            "content": "Appointments can be scheduled by calling our office, using the patient portal, or through our mobile app. We request 24-hour notice for cancellations to avoid a $50 cancellation fee. Same-day appointments are available for urgent concerns. New patient appointments typically last 45 minutes, while follow-up visits are 20-30 minutes.",
            "category": "administrative",
            "source": "patient_guide"
        },
        
        # Moderate - Common Conditions
        {
            "id": "3",
            "title": "Common Cold vs Influenza: Diagnosis and Management",
            "content": "The common cold is caused by rhinoviruses and typically presents with gradual onset of runny nose, sore throat, cough, and mild fatigue. Symptoms last 7-10 days and are self-limiting. Influenza (flu) is caused by influenza viruses and presents with sudden onset of high fever (101-104°F), severe body aches, headache, dry cough, and extreme fatigue. Flu symptoms are more severe and can last 1-2 weeks. Treatment for cold is supportive (rest, fluids, over-the-counter medications). Flu may require antiviral medications (oseltamivir, zanamivir) if started within 48 hours of symptom onset. Annual flu vaccination is the best prevention.",
            "category": "clinical",
            "source": "clinical_guidelines"
        },
        {
            "id": "4",
            "title": "Diabetes Mellitus: Diagnosis, Symptoms, and Monitoring",
            "content": "Diabetes mellitus is a metabolic disorder characterized by hyperglycemia. Type 1 diabetes results from autoimmune destruction of pancreatic beta cells, requiring insulin therapy. Type 2 diabetes involves insulin resistance and progressive beta cell dysfunction. Common symptoms include polyuria (frequent urination), polydipsia (excessive thirst), polyphagia (increased hunger), unexplained weight loss, fatigue, and blurred vision. Diagnosis is made with fasting glucose ≥126 mg/dL, HbA1c ≥6.5%, or 2-hour glucose ≥200 mg/dL during oral glucose tolerance test. Management includes lifestyle modifications (diet, exercise), oral medications (metformin, sulfonylureas, SGLT2 inhibitors), and insulin therapy when needed. Target HbA1c <7% for most patients. Regular monitoring for complications including retinopathy, nephropathy, neuropathy, and cardiovascular disease is essential.",
            "category": "clinical",
            "source": "endocrinology_manual"
        },
        {
            "id": "5",
            "title": "Hypertension: Classification, Evaluation, and Treatment Guidelines",
            "content": "Hypertension is defined as systolic BP ≥130 mmHg or diastolic BP ≥80 mmHg. Classification: Normal (<120/80), Elevated (120-129/<80), Stage 1 (130-139 or 80-89), Stage 2 (≥140 or ≥90). Secondary causes should be evaluated including renal disease, primary aldosteronism, pheochromocytoma, and Cushing's syndrome. Initial evaluation includes ECG, urinalysis, basic metabolic panel, lipid panel, and assessment of target organ damage. First-line medications include ACE inhibitors, ARBs, calcium channel blockers, and thiazide diuretics. Lifestyle modifications are essential: weight loss, DASH diet, sodium restriction (<2300 mg/day), regular exercise (150 min/week), and alcohol moderation. Target BP <130/80 for most adults.",
            "category": "clinical",
            "source": "cardiology_guidelines"
        },
        
        # Complex - Advanced Medical Topics
        {
            "id": "6",
            "title": "Congestive Heart Failure: Pathophysiology and Classification",
            "content": "Heart failure (HF) is a clinical syndrome resulting from structural or functional cardiac impairment leading to reduced cardiac output or elevated intracardiac pressures. Pathophysiology involves activation of compensatory mechanisms: renin-angiotensin-aldosterone system (RAAS), sympathetic nervous system, and natriuretic peptides. Left ventricular dysfunction leads to increased preload, decreased contractility, and elevated pulmonary pressures. Classification systems include: NYHA functional class (I-IV based on symptoms), ACC/AHA stages (A-D based on structural changes), and HF with reduced ejection fraction (HFrEF, LVEF ≤40%), mildly reduced (HFmrEF, 41-49%), or preserved (HFpEF, ≥50%). Common etiologies include ischemic heart disease, hypertension, valvular disease, and cardiomyopathies. Key symptoms: dyspnea, orthopnea, paroxysmal nocturnal dyspnea, peripheral edema, and fatigue.",
            "category": "clinical",
            "source": "cardiology_textbook"
        },
        {
            "id": "7",
            "title": "Heart Failure Management: Pharmacotherapy and Device Therapy",
            "content": "HFrEF pharmacotherapy includes guideline-directed medical therapy (GDMT): ACE inhibitors or ARBs reduce mortality by 20-30% through RAAS inhibition; beta-blockers (carvedilol, metoprolol succinate, bisoprolol) reduce mortality by 35% through sympathetic blockade; mineralocorticoid receptor antagonists (spironolactone, eplerenone) reduce mortality by 30%; SGLT2 inhibitors (dapagliflozin, empagliflozin) reduce HF hospitalizations by 30%; ARNI (sacubitril/valsartan) superior to ACE inhibitors with 20% mortality reduction. Diuretics for congestion management (loop diuretics for volume overload). Device therapy: Implantable cardioverter-defibrillator (ICD) for LVEF ≤35% and life expectancy >1 year reduces sudden cardiac death by 23%; Cardiac resynchronization therapy (CRT) for LVEF ≤35%, QRS ≥150ms, and LBBB improves symptoms and reduces mortality by 36%. Advanced therapies include mechanical circulatory support (LVAD) and heart transplantation for refractory HF.",
            "category": "clinical",
            "source": "cardiology_therapeutics"
        },
        {
            "id": "8",
            "title": "Acute Coronary Syndrome: Pathophysiology and Management",
            "content": "Acute coronary syndrome (ACS) encompasses unstable angina (UA), non-ST-elevation myocardial infarction (NSTEMI), and ST-elevation myocardial infarction (STEMI). Pathophysiology: atherosclerotic plaque rupture → platelet activation and aggregation → thrombus formation → coronary occlusion. STEMI represents complete coronary occlusion requiring immediate reperfusion. Initial management: aspirin 325mg, P2Y12 inhibitor (ticagrelor or prasugrel preferred over clopidogrel), anticoagulation (heparin or enoxaparin), beta-blocker, statin, and nitrates for symptom relief. STEMI treatment: primary PCI within 90 minutes of first medical contact or fibrinolysis if PCI not available within 120 minutes. NSTEMI/UA: risk stratification using TIMI or GRACE score; high-risk patients require early invasive strategy (angiography within 24 hours). Post-MI management: dual antiplatelet therapy (DAPT) for 12 months, high-intensity statin (atorvastatin 80mg), ACE inhibitor, beta-blocker, and cardiac rehabilitation.",
            "category": "clinical",
            "source": "emergency_medicine"
        },
        {
            "id": "9",
            "title": "Pharmacokinetics: Drug Metabolism and CYP450 Interactions",
            "content": "Cytochrome P450 (CYP450) enzymes are responsible for metabolism of >75% of medications. Major isoforms: CYP3A4/5 (50% of drugs), CYP2D6 (25%), CYP2C9/19, CYP1A2. Drug interactions occur through enzyme inhibition or induction. Strong CYP3A4 inhibitors (ketoconazole, ritonavir, clarithromycin) increase substrate concentrations, requiring dose reduction of sensitive drugs (statins, immunosuppressants, calcium channel blockers). CYP3A4 inducers (rifampin, phenytoin, carbamazepine) decrease substrate levels, potentially causing therapeutic failure. CYP2D6 genetic polymorphisms affect 5-10% of population: poor metabolizers have increased drug levels and adverse effects with codeine, tramadol, antidepressants; ultra-rapid metabolizers have reduced efficacy. Warfarin is metabolized by CYP2C9; polymorphisms and interactions with amiodarone, fluconazole require INR monitoring and dose adjustments. Clinical implications require careful medication review, dose adjustments, and therapeutic drug monitoring.",
            "category": "clinical",
            "source": "pharmacology_textbook"
        },
        {
            "id": "10",
            "title": "Differential Diagnosis: Acute Abdominal Pain",
            "content": "Systematic approach to acute abdominal pain by anatomical location: Right Upper Quadrant (RUQ) - cholecystitis, hepatitis, hepatic abscess, right lower lobe pneumonia, peptic ulcer disease. Left Upper Quadrant (LUQ) - splenic infarct/rupture, gastritis, pancreatitis, left lower lobe pneumonia. Right Lower Quadrant (RLQ) - appendicitis, ovarian torsion, ectopic pregnancy, inflammatory bowel disease (Crohn's), kidney stone, testicular torsion. Left Lower Quadrant (LLQ) - diverticulitis, sigmoid volvulus, ovarian pathology, ectopic pregnancy, inflammatory bowel disease. Epigastric - peptic ulcer disease, pancreatitis, myocardial infarction (atypical), GERD, gastritis. Suprapubic - cystitis, urinary retention, uterine pathology. Diffuse - gastroenteritis, bowel obstruction, mesenteric ischemia, peritonitis, diabetic ketoacidosis. Red flags requiring immediate evaluation: hemodynamic instability, peritoneal signs, severe constant pain, abdominal distension, absence of bowel sounds. Initial workup: CBC, comprehensive metabolic panel, lipase, urinalysis, pregnancy test (females of reproductive age), imaging (ultrasound for RUQ/pelvic, CT for complex cases).",
            "category": "clinical",
            "source": "emergency_medicine"
        },
        {
            "id": "11",
            "title": "Vaccine Mechanisms: Immunology and Efficacy",
            "content": "Vaccines induce active immunity through presentation of antigens to the immune system, stimulating both humoral (antibody-mediated) and cell-mediated immune responses. Vaccine types: Live attenuated vaccines (MMR, varicella) contain weakened pathogens that replicate, providing robust immunity but contraindicated in immunocompromised patients. Inactivated vaccines (polio, hepatitis A) contain killed pathogens requiring adjuvants and booster doses. Subunit vaccines (hepatitis B, HPV) contain specific antigens with excellent safety profiles. mRNA vaccines (COVID-19) deliver genetic instructions for antigen production, inducing strong immune responses without live virus. Vaccine efficacy depends on antigen presentation to dendritic cells → T cell activation (CD4+ helper cells, CD8+ cytotoxic cells) → B cell activation and antibody production (IgG, IgM, IgA) → formation of memory cells for long-term protection. Herd immunity occurs when >80-95% of population is vaccinated (varies by disease), protecting vulnerable individuals who cannot be vaccinated.",
            "category": "clinical",
            "source": "immunology_textbook"
        },
        {
            "id": "12",
            "title": "Clinical Trial Evidence: PARADIGM-HF and DAPA-HF",
            "content": "PARADIGM-HF Trial: Prospective comparison of ARNI versus ACEI to Determine Impact on Global Mortality and Morbidity in Heart Failure. Design: randomized, double-blind trial comparing sacubitril/valsartan (ARNI) vs enalapril in 8442 patients with HFrEF (LVEF ≤40%, NYHA II-IV). Primary outcome: cardiovascular death or HF hospitalization occurred in 21.8% (ARNI) vs 26.5% (enalapril), hazard ratio 0.80 (95% CI 0.73-0.87, p<0.001). Secondary outcomes: cardiovascular mortality reduced by 20%, all-cause mortality by 16%, HF hospitalizations by 21%. NNT to prevent one primary outcome event = 21 patients. DAPA-HF Trial: Dapagliflozin and Prevention of Adverse Outcomes in Heart Failure. Design: randomized, double-blind, placebo-controlled trial of dapagliflozin 10mg daily in 4744 patients with HFrEF (LVEF ≤40%, NYHA II-IV) with or without diabetes. Primary outcome: cardiovascular death or worsening HF occurred in 16.3% (dapagliflozin) vs 21.2% (placebo), hazard ratio 0.74 (95% CI 0.65-0.85, p<0.001). Benefits consistent regardless of diabetes status. NNT = 21. Both trials demonstrate substantial mortality and morbidity benefits, establishing ARNI and SGLT2 inhibitors as cornerstone therapies in HFrEF.",
            "category": "clinical",
            "source": "evidence_based_medicine"
        }
    ]
    
    # Upload documents
    try:
        result = search_client.upload_documents(documents=documents)
        success_count = sum(1 for r in result if r.succeeded)
        print(f"✓ Uploaded {success_count}/{len(documents)} documents to index")
        
        # Show document summary
        print("\n📚 Document Summary:")
        for doc in documents:
            print(f"  - {doc['category'].upper()}: {doc['title']}")
        
    except Exception as e:
        print(f"✗ Error uploading documents: {str(e)}")
        raise

if __name__ == "__main__":
    print("🔧 Setting up Azure AI Search Index for Medical Knowledge Base\n")
    
    # Check environment variables
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_key = os.getenv("SEARCH_KEY")
    
    if not search_endpoint or not search_key:
        print("✗ Error: SEARCH_ENDPOINT and SEARCH_KEY must be set in .env file")
        exit(1)
    
    print(f"📍 Search Endpoint: {search_endpoint}")
    print(f"📇 Index Name: medical-kb\n")
    
    # Create index and populate
    create_index()
    print()
    populate_index()
    
    print("\n✅ Setup complete! The RAG pipeline is now ready for testing.")
    print("\n💡 Try these queries:")
    print("   Simple: 'What are your office hours?'")
    print("   Moderate: 'What's the difference between a cold and the flu?'")
    print("   Complex: 'Explain heart failure treatment with clinical trial evidence'")
