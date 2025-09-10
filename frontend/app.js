const { useMemo, useState, useEffect, useRef } = React;

// ---- Data (same as before) ---------------------------------------------------
const STEPS = ["Reentry Care Plan", "Health Risk Assessment", "Warm Handoff"];

const REENTRY_SECTIONS = [
  {
    title: "Personal Identification & Demographics",
    tables: [
      "Name of the youth (CM)",
      "Race/Ethnicity (Excel)",
      "Telephone (Excel)",
      "Residential Address (Excel)",
      "Emergency contacts (Excel)",
      "Identification documents (Excel)",
    ],
  },
  { title: "Release & Legal Information", tables: ["Actual release date (CM)", "Court dates (CM)"] },
  {
    title: "Healthcare & Medical Management",
    tables: [
      "Medi-Cal ID Number (CM)",
      "Medi-Cal health plan assigned (Excel)",
      "Health Screenings (Excel)",
      "Health Assessments (Excel)",
      "Chronic Conditions (Excel)",
      "Prescribed Medications (Excel)",
      "Clinical Assessments (Excel)",
      "Screenings (Excel)",
      "Primary physician contacts (Excel)",
      "Durable Medical Equipment (SQL)",
    ],
  },
  {
    title: "Treatment History & Mental Health",
    tables: [
      "Treatment History (mental health, physical health, substance use) (Excel)",
    ],
  },
  { title: "Healthcare Coordination & Appointments", tables: ["Scheduled Appointments (CM)"] },
  {
    title: "Basic Life Needs & Support",
    tables: [
      "Housing (SQL)",
      "Food & Clothing (Excel)",
      "Transportation (Excel)",
      "Income and benefits (SQL)",
      "Home Modifications (SQL)",
    ],
  },
  { title: "Employment & Life Skills", tables: ["Employment (CM)", "Life skills (SQL)"] },
  { title: "Family & Social Support", tables: ["Family and children (SQL)"] },
  { title: "Service Coordination & Referrals", tables: ["Service referrals (SQL)"] },
];

const ADULT_SECTIONS = [
  { title: "Core Screening & Identification", tables: [
    "adult_screening",
    "adult_admission_screening", 
    "adult_level_of_consciousness",
  ]},
  { title: "Physical Health & Medical Assessment", tables: [
    "adult_vital_signs",
    "adult_observation",
    "adult_past_medical_questionnaire",
    "adult_allergies_and_diet",
    "adult_dental_screening",
  ]},
  { title: "Chronic Medical Conditions", tables: [
    "adult_diabetes",
    "adult_hypertension", 
    "adult_heart_condition",
    "adult_asthma",
    "adult_copd",
    "adult_kidney_disease",
    "adult_traumatic_brain_injury",
    "adult_seizure_disorder",
    "adult_developmental_disability",
    "adult_special_accommodations",
  ]},
  { title: "Medications & Treatments", tables: [
    "adult_additional_medication",
  ]},
  { title: "Infectious Disease Screening", tables: [
    "adult_infectious_disease_screening",
  ]},
  { title: "Mental Health & Suicide Risk", tables: [
    "adult_mental_health_screening",
    "adult_suicide_risk_scale",
    "adult_suicide_additional_screening",
  ]},
  { title: "Substance Use Assessment", tables: [
    "adult_substance_use",
  ]},
  { title: "Safety & Security Screening", tables: [
    "adult_prea_screening",
  ]},
  { title: "Special Population Assessment", tables: [
    "adult_juvenile_specific",
  ]},
  { title: "Patient Education & Documentation", tables: [
    "adult_patient_education",
    "adult_release_information",
  ]},
  { title: "Clinical Disposition & Outcomes", tables: [
    "adult_disposition",
    "adult_acknowledgment",
  ]},
];

const JUVENILE_SECTIONS = [
  { title: "Core Assessment & Identification", tables: [
    "juvenile_assessment",
    "juvenile_confidentiality_triggers",
  ]},
  { title: "Family & Social Context", tables: [
    "juvenile_family_history", 
    "juvenile_relationships",
  ]},
  { title: "Education & Development", tables: [
    "juvenile_education_employment",
    "juvenile_developmental_medical",
  ]},
  { title: "Mental Health Assessment", tables: [
    "juvenile_mental_health_history",
    "juvenile_observations", 
    "juvenile_mental_status_exam",
  ]},
  { title: "Substance Use History", tables: [
    "juvenile_substance_use_history",
  ]},
  { title: "Risk Assessment & Safety", tables: [
    "juvenile_risk_factors",
    "juvenile_protective_factors",
    "juvenile_risk_level",
  ]},
  { title: "Treatment Planning & Follow-up", tables: [
    "juvenile_follow_up_plan",
  ]},
];

const GENERIC_SECTIONS = [
  { title: "General", tables: ["field_1", "field_2"] },
];


// Candidate pools
const REENTRY_CANDIDATES = [
  { id: "", name: "Choose..." },
  { id: "r1", name: "John Doe" },
  { id: "r2", name: "Jane Smith" },
];

const ADULT_CANDIDATES = [
  { id: "", name: "Choose..." },
  { id: "a1", name: "James Hernandez" },
  { id: "a2", name: "Maria Sanchez" },
  { id: "a3", name: "Michael Nguyen" },
];

const JUVENILE_CANDIDATES = [
  { id: "", name: "Choose..." },
  { id: "j1", name: "Isabella Martinez" },
  { id: "j2", name: "Matthew Johnson" },
  { id: "j3", name: "Sofia Lee" },
];

const DEFAULT_CANDIDATES = [
  { id: "", name: "Choose..." },
  { id: "1", name: "Alex Johnson" },
  { id: "2", name: "Brianna Lee" },
  { id: "3", name: "Carlos Sanchez" },
];

function buildTemplate(sections) {
  return sections.map((s, i) => ({
    id: `panel-${i + 1}`,
    title: s.title,
    fields: s.tables.map((t) => ({ id: t, label: t })),
  }));
}

// ---- UI Components ----
function Step({ selected, label, onClick }) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      onClick={onClick}
      className={`flex items-center gap-3 rounded-full px-7 py-3 text-base md:text-lg font-semibold transition focus:outline-none ${
        selected ? "bg-emerald-500 text-white shadow" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
      }`}
    >
      {label}
    </button>
  );
}

function Card({ children, compact }) {
  return (
    <div className={`rounded-2xl border border-gray-200 bg-white shadow-sm hover:shadow-md transition ${
      compact ? "p-4 inline-block w-auto" : "p-6"
    }`}>
      {children}
    </div>
  );
}

function SearchInput({ value, onChange, placeholder = "Search..." }) {
  return (
    <div className="flex items-center rounded-xl border border-gray-300 bg-white px-3 shadow focus-within:ring-2 focus-within:ring-emerald-500">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5 text-gray-500">
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M10 18a8 8 0 100-16 8 8 0 000 16z" />
      </svg>
      <input 
        value={value} 
        onChange={(e) => onChange(e.target.value)} 
        placeholder={placeholder} 
        className="w-full bg-transparent p-2 text-sm outline-none" 
      />
    </div>
  );
}

function CandidateSelect({ list, value, onChange, placeholder = "Choose or enter a name..." }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  const filtered = useMemo(() => {
    if (!value) return list.filter(c => c.id); // Show all except "Choose..."
    return list.filter((c) =>
      c.id && c.name.toLowerCase().includes(value.toLowerCase())
    );
  }, [list, value]);

  // Effect to handle clicks outside the component
  useEffect(() => {
    function handleOutsideClick(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [containerRef]);

  const handleInputChange = (e) => {
    onChange(e.target.value);
    if (!isOpen) {
      setIsOpen(true);
    }
  };

  const handleOptionClick = (candidate) => {
    onChange(candidate.name);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={containerRef}>
      <div className="flex items-center rounded-xl border border-gray-300 bg-white px-3 shadow focus-within:ring-2 focus-within:ring-emerald-500">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5 text-gray-500">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
        </svg>
        <input 
          value={value}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder} 
          className="w-full bg-transparent p-2 text-sm outline-none" 
        />
         <button type="button" onClick={() => setIsOpen(s => !s)} className="text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
              <path d="M6 9l6 6 6-6" />
            </svg>
        </button>
      </div>

      {isOpen && (
        <div className="absolute z-10 mt-2 w-full overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg">
          <div className="max-h-60 overflow-y-auto p-1">
            {filtered.length > 0 ? filtered.map((c) => (
              <button
                key={c.id}
                onClick={() => handleOptionClick(c)}
                className="w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-emerald-50"
              >
                {c.name}
              </button>
            )) : (
                 <div className="px-3 py-2 text-sm text-gray-500">No matches found. Your entry will be saved.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ErrorAlert({ message, onClose }) {
  if (!message) return null;
  
  return (
    <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-red-900">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">Error:</span>
          <span>{message}</span>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-red-400 hover:text-red-600">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

function SuccessAlert({ message, onClose }) {
  if (!message) return null;
  
  return (
    <div className="mt-4 rounded-xl border border-green-200 bg-green-50 p-4 text-green-900">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">Success:</span>
          <span>{message}</span>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-green-400 hover:text-green-600">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

// ---- Main Component ----
function ReentryCarePlanUI() {
  const [activeStep, setActiveStep] = useState(0);
  const [assessmentType, setAssessmentType] = useState("");
  const [candidateName, setCandidateName] = useState('');
  const [candidateProfiles, setCandidateProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState('');
  const [loadingProfiles, setLoadingProfiles] = useState(false);
  const [schemaQuery, setSchemaQuery] = useState("");
  const [checked, setChecked] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const baseTemplate = useMemo(() => {
    const hasCandidate = !!candidateName.trim();
    if (STEPS[activeStep] === "Reentry Care Plan") {
      if (!hasCandidate) return [];
      return buildTemplate(REENTRY_SECTIONS);
    }
    if (STEPS[activeStep] === "Health Risk Assessment") {
      if (!assessmentType || !hasCandidate) return [];
      if (assessmentType === "Adult_Receiving_Screening") return buildTemplate(ADULT_SECTIONS);
      if (assessmentType === "Juvenile_MH_Screening") return buildTemplate(JUVENILE_SECTIONS);
      return [];
    }
    return buildTemplate(GENERIC_SECTIONS);
  }, [activeStep, assessmentType, candidateName]);

  const filteredTemplate = useMemo(() => {
    const q = schemaQuery.trim().toLowerCase();
    if (!q) return baseTemplate;
    return baseTemplate
      .map((p) => ({ ...p, fields: p.fields.filter((f) => f.label.toLowerCase().includes(q)) }))
      .filter((p) => p.fields.length > 0);
  }, [baseTemplate, schemaQuery]);

  const candidatePool = useMemo(() => {
    if (STEPS[activeStep] === "Reentry Care Plan") return REENTRY_CANDIDATES;
    if (STEPS[activeStep] === "Health Risk Assessment") {
      if (assessmentType === "Adult_Receiving_Screening") return ADULT_CANDIDATES;
      if (assessmentType === "Juvenile_MH_Screening") return JUVENILE_CANDIDATES;
      return [{ id: "", name: "Choose..." }];
    }
    return DEFAULT_CANDIDATES;
  }, [activeStep, assessmentType]);

  // Reset states when template or candidate pool changes
  useEffect(() => setChecked({}), [baseTemplate, candidatePool]);

  // Reset fields on step/type change
  useEffect(() => {
    setCandidateName("");
    setCandidateProfiles([]);
    setSelectedProfile("");
  }, [activeStep, assessmentType]);

  // Clear messages when context changes
  useEffect(() => {
    setError("");
    setSuccess("");
  }, [activeStep, assessmentType, candidateName, selectedProfile]);

  const allFieldIds = useMemo(() => 
    filteredTemplate.flatMap((p) => p.fields.map((f) => f.id)), 
    [filteredTemplate]
  );
  
  const allSelected = allFieldIds.length > 0 && allFieldIds.every((id) => checked[id]);
  
  const toggleAll = (next) => setChecked(Object.fromEntries(allFieldIds.map((id) => [id, next])));
  const toggle = (id) => setChecked((prev) => ({ ...prev, [id]: !prev[id] }));

  // Handle profile selection - update candidate name when profile is selected
  const handleProfileSelection = (medicalId) => {
    setSelectedProfile(medicalId);
    if (medicalId) {
      const selectedProfileData = candidateProfiles.find(profile => profile.medical_id === medicalId);
      if (selectedProfileData) {
        // Update candidate name to full display text including ID
        setCandidateName(selectedProfileData.display_text);
      }
    }
  };

  // Fetch candidate profiles when candidate name changes (only for Reentry Care Plan)
  useEffect(() => {
    const fetchCandidates = async () => {
      // Only fetch candidates for Reentry Care Plan
      if (STEPS[activeStep] !== "Reentry Care Plan" || !candidateName.trim()) {
        setCandidateProfiles([]);
        setSelectedProfile("");
        return;
      }

      try {
        setLoadingProfiles(true);
        setError("");
        
        const response = await fetch("http://localhost:5000/get_candidates_by_name", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ candidate_name: candidateName }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: `Server error: ${response.status}` }));
          throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        const data = await response.json();
        const profiles = data.candidates || [];
        setCandidateProfiles(profiles);
        
        // Auto-select if only one profile found
        if (profiles.length === 1) {
          setSelectedProfile(profiles[0].medical_id);
          // Update candidate name to full display text including ID
          setCandidateName(profiles[0].display_text);
        } else {
          setSelectedProfile(""); // Reset selection when multiple profiles loaded
          // Don't update candidate name here - keep user input until they select
        }
        
      } catch (err) {
        console.error("Error fetching candidates:", err);
        setError(`Failed to fetch candidate profiles: ${err.message}`);
        setCandidateProfiles([]);
        setSelectedProfile("");
      } finally {
        setLoadingProfiles(false);
      }
    };

    // Debounce the API call
    const timeoutId = setTimeout(fetchCandidates, 500);
    return () => clearTimeout(timeoutId);
  }, [candidateName, activeStep]);

  async function generate() {
    setError("");
    setSuccess("");
    
    const step = STEPS[activeStep];
    const selectedFields = Object.entries(checked).filter(([, v]) => v).map(([k]) => k);
    
    // Validation
    if (selectedFields.length === 0) {
      setError("Please select at least one field to generate the document.");
      return;
    }

    const finalCandidateName = candidateName.trim();
    if (!finalCandidateName) {
        setError("Please choose or enter a candidate name.");
        return;
    }
    
    // If multiple profiles are available and we're in Reentry Care Plan, ensure one is selected
    if (STEPS[activeStep] === "Reentry Care Plan" && candidateProfiles.length > 1 && !selectedProfile) {
        setError("Please select a correct profile from the list.");
        return;
    }

    try {
      setLoading(true);
      
      let endpoint = "";
      let filename = "";
      
      if (step === "Reentry Care Plan") {
        endpoint = "http://localhost:5000/generate_reentry_care_plan";
        // endpoint = "/generate_reentry_care_plan";
        filename = `${finalCandidateName}_reentry_care_plan.docx`;
      } else if (step === "Health Risk Assessment") {
        if (!assessmentType) {
          setError("Please choose an Assessment Type first.");
          return;
        }
        
        if (assessmentType === "Adult_Receiving_Screening") {
          endpoint = "http://localhost:5000/generate_hra_adult";
          // endpoint = "/generate_hra_adult";
          filename = `${finalCandidateName}_adult_hra.docx`;
        } else if (assessmentType === "Juvenile_MH_Screening") {
          endpoint = "http://localhost:5000/generate_hra_juvenile";
          // endpoint = "/generate_hra_juvenile";
          filename = `${finalCandidateName}_juvenile_hra.docx`;
        } else {
          setError("Unknown assessment type selected.");
          return;
        }
      } else {
        setError("Warm Handoff generation is not yet implemented.");
        return;
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          selected_fields: selectedFields, 
          candidate_name: finalCandidateName,
          selected_profile: selectedProfile
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: `Server error: ${response.status}` }));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setSuccess(`Successfully generated ${step} document for ${finalCandidateName}!`);
      
    } catch (err) {
      console.error("Generation error:", err);
      setError(err.message || "An unexpected error occurred while generating the document.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full bg-gray-50 p-6 md:p-10">
      {/* Logo Section */}
      <div className="flex justify-center mb-8">
        <img 
          src="/image/image.png" 
          alt="Company Logo" 
          className="app-logo"
          onError={(e) => {
            e.target.style.display = 'none';
            console.log('Logo not found at /image/image.png');
          }}
        />
      </div>

      {/* Heading & tagline (below logo) */}
      <div className="text-center mb-6">
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-gray-900">
          Agentic GenAI Reentry Platform
        </h2>
        <p className="mt-1 text-base md:text-lg text-gray-700">
          Automates coordinated behavioral health for justice-involved people
        </p>
      </div>

      <hr className="border-gray-200 mb-8" />

      {/* Steps */}
      <div className="flex justify-center gap-6 mb-10">
        {STEPS.map((s, i) => (
          <Step key={s} selected={i === activeStep} label={s} onClick={() => setActiveStep(i)} />
        ))}
      </div>

      <Card>
        <div className="mx-auto max-w-6xl">
          <h1 className="text-center text-3xl font-bold tracking-tight text-gray-900 mb-6">
            {STEPS[activeStep]}
          </h1>

          {/* HRA controls */}
          {STEPS[activeStep] === "Health Risk Assessment" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Assessment Type</label>
                <select
                  value={assessmentType}
                  onChange={(e) => setAssessmentType(e.target.value)}
                  className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="">Choose...</option>
                  <option value="Adult_Receiving_Screening">Adult Receiving Screening</option>
                  <option value="Juvenile_MH_Screening">Juvenile MH Screening</option>
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Candidate</label>
                <CandidateSelect list={candidatePool} value={candidateName} onChange={setCandidateName} />
              </div>
            </div>
          )}

          {/* Reentry controls */}
          {STEPS[activeStep] === "Reentry Care Plan" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Candidate</label>
                <CandidateSelect list={candidatePool} value={candidateName} onChange={setCandidateName} />
              </div>
              {candidateName.trim() && candidateProfiles.length > 1 && (
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Select Correct Profile ({candidateProfiles.length} found)
                    {loadingProfiles && <span className="text-xs text-gray-500 ml-1">(Loading...)</span>}
                  </label>
                  <select
                    value={selectedProfile}
                    onChange={(e) => handleProfileSelection(e.target.value)}
                    disabled={loadingProfiles}
                    className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    <option value="">Choose profile...</option>
                    {candidateProfiles.map((profile, index) => (
                      <option key={index} value={profile.medical_id}>
                        {profile.display_text}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              {candidateName.trim() && candidateProfiles.length === 1 && (
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Profile Status</label>
                  <div className="w-full rounded-xl border border-green-200 bg-green-50 px-3 py-2 text-green-800">
                    ✓ Single profile found and selected: {candidateProfiles[0].display_text}
                  </div>
                </div>
              )}
              {candidateName.trim() && !loadingProfiles && candidateProfiles.length === 0 && (
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Profile Status</label>
                  <div className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-gray-600">
                    No profiles found in database - using entered name
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Alert Messages */}
          <ErrorAlert message={error} onClose={() => setError("")} />

          {/* Empty states */}
          {STEPS[activeStep] === "Reentry Care Plan" && !candidateName.trim() && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
              Please choose or enter a candidate to view Reentry fields.
            </div>
          )}
          {STEPS[activeStep] === "Health Risk Assessment" && !assessmentType && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
              Please choose an <span className="font-semibold">Assessment Type</span> to continue.
            </div>
          )}
          {STEPS[activeStep] === "Health Risk Assessment" && !!assessmentType && !candidateName.trim() && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
              Please choose or enter a <span className="font-semibold">Candidate</span> to view HRA fields.
            </div>
          )}

          {/* Search */}
          {baseTemplate.length > 0 && (
            <div className="mt-6">
              <SearchInput value={schemaQuery} onChange={setSchemaQuery} placeholder="Search schema..." />
            </div>
          )}

          {/* Select all */}
          {baseTemplate.length > 0 && (
            <div className="mt-6 flex items-center gap-3">
              <input 
                id="select-all" 
                type="checkbox" 
                checked={allSelected} 
                onChange={(e) => toggleAll(e.target.checked)} 
                className="h-5 w-5 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500" 
              />
              <label htmlFor="select-all" className="text-sm text-gray-700">
                Select all ({filteredTemplate.flatMap(p => p.fields).length} fields)
              </label>
            </div>
          )}

          {/* Cards */}
          {baseTemplate.length > 0 && (
            <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
              {filteredTemplate.map((panel) => (
                <Card key={panel.id} compact={panel.fields.length === 1}>
                  <div className="text-lg font-semibold text-emerald-700 mb-3">
                    {panel.title}
                  </div>
                  <div className="space-y-3">
                    {panel.fields.map((f) => (
                      <div key={f.id} className="flex items-center gap-3">
                        <input 
                          type="checkbox" 
                          id={f.id} 
                          checked={!!checked[f.id]} 
                          onChange={() => toggle(f.id)} 
                          className="h-5 w-5 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500" 
                        />
                        <label htmlFor={f.id} className="text-sm text-gray-700">
                          {f.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Primary action */}
          {baseTemplate.length > 0 && (
            <div className="mt-8 flex justify-center">
              <button 
                onClick={generate} 
                disabled={loading || Object.values(checked).filter(Boolean).length === 0} 
                className="rounded-xl bg-emerald-500 px-8 py-3 text-base font-semibold text-white shadow hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </div>
                ) : (
                  `Generate ${STEPS[activeStep]}`
                )}
              </button>
            </div>
          )}

          {/* Success Message - Appears below the button */}
          <SuccessAlert message={success} onClose={() => setSuccess("")} />

          {/* Progress indicator when loading */}
          {loading && (
            <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-4">
              <div className="flex items-center gap-3">
                <svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div>
                  <div className="font-medium text-blue-900">Processing your request...</div>
                  <div className="text-sm text-blue-700">
                    {STEPS[activeStep] === "Health Risk Assessment" 
                      ? "Fetching data using AI tools and generating document..."
                      : "Generating document from selected fields..."
                    }
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

ReactDOM.render(<ReentryCarePlanUI />, document.getElementById('root'));
