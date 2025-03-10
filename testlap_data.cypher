// Create constraints for testlap project
CREATE CONSTRAINT testlap_anatomy_id IF NOT EXISTS ON (a:TestlapAnatomy) ASSERT a.id IS UNIQUE;
CREATE CONSTRAINT testlap_instrument_id IF NOT EXISTS ON (i:TestlapInstrument) ASSERT i.id IS UNIQUE;
CREATE CONSTRAINT testlap_phase_id IF NOT EXISTS ON (p:TestlapPhase) ASSERT p.id IS UNIQUE;
CREATE CONSTRAINT testlap_action_name IF NOT EXISTS ON (a:TestlapAction) ASSERT a.name IS UNIQUE;

// Create Anatomy Nodes
CREATE (:TestlapAnatomy {id: 1, name: "Uterus", description: "Female reproductive organ"});

// Create Instrument Nodes
CREATE (:TestlapInstrument {id: 1, name: "Grasping forceps", 
                    description: "Toothed instrument for tissue manipulation", 
                    combo_instruments: [2,4], 
                    action_type: "Grasping/Retraction", 
                    features: "Serrated jaws, 5mm diameter"});

CREATE (:TestlapInstrument {id: 2, name: "LigaSure", 
                    description: "Vessel sealing system with feedback control", 
                    combo_instruments: [1,3], 
                    action_type: "Vessel sealing/Cutting", 
                    features: "Advanced bipolar energy, 10mm shaft"});

CREATE (:TestlapInstrument {id: 3, name: "Dissecting and grasping forceps", 
                    description: "Dual-purpose instrument for blunt dissection", 
                    combo_instruments: [2,4], 
                    action_type: "Dissection/Grasping", 
                    features: "Angulated tip, ratcheted handle"});

CREATE (:TestlapInstrument {id: 4, name: "Electric hook", 
                    description: "Electrosurgical cutting instrument", 
                    combo_instruments: [1,3], 
                    action_type: "Precise dissection/Cutting", 
                    features: "Monopolar energy, L-shaped tip"});

// Create Phase Nodes with Temporal Context
CREATE (:TestlapPhase {id: 1, 
               name: "Preparation", 
               definition: "Patient positioning and pneumoperitoneum establishment", 
               duration: "5-15 min", 
               start_features: ["General anesthesia confirmed", "Trocar placements begun"], 
               end_features: ["Pneumoperitoneum maintained at 12mmHg", "All trocars positioned"], 
               instrument_ids: [1,3]});

CREATE (:TestlapPhase {id: 2, 
               name: "Dividing Ligament and Peritoneum", 
               definition: "Initial dissection of broad/round ligaments", 
               duration: "10-25 min", 
               start_features: ["First peritoneal incision with electric hook (ID4)"], 
               end_features: ["Complete exposure of uterine vessels"], 
               instrument_ids: [1,3,4]});

CREATE (:TestlapPhase {id: 3, 
               name: "Dividing Uterine Vessels and Ligament", 
               definition: "Sealing and transection of vascular pedicles", 
               duration: "15-30 min", 
               start_features: ["Application of LigaSure (ID2) to vascular bundle"], 
               end_features: ["Complete devascularization of uterus"], 
               instrument_ids: [1,2,3]});

CREATE (:TestlapPhase {id: 4, 
               name: "Transecting the Vagina", 
               definition: "Circumferential vaginal cuff creation", 
               duration: "8-15 min", 
               start_features: ["Colpotomy cup placement"], 
               end_features: ["Complete separation from cervical stump"], 
               instrument_ids: [2,4]});

CREATE (:TestlapPhase {id: 5, 
               name: "Specimen Removal", 
               definition: "Extraction through vaginal canal or morcellation", 
               duration: "5-20 min", 
               start_features: ["Specimen bag deployment"], 
               end_features: ["Complete removal confirmed"], 
               instrument_ids: [1,3]});

CREATE (:TestlapPhase {id: 6, 
               name: "Suturing", 
               definition: "Vaginal cuff closure under laparoscopic guidance", 
               duration: "10-25 min", 
               start_features: ["First suture bite through vaginal mucosa"], 
               end_features: ["Watertight closure confirmed"], 
               instrument_ids: [1,3]});

CREATE (:TestlapPhase {id: 7, 
               name: "Washing", 
               definition: "Final irrigation and hemostasis check", 
               duration: "3-8 min", 
               start_features: ["Saline irrigation begun"], 
               end_features: ["Clear effluent with no active bleeding"], 
               instrument_ids: [3]});

// Create Phase Sequence Relationships
MATCH (p1:TestlapPhase {id:1}), (p2:TestlapPhase {id:2})
CREATE (p1)-[:TESTLAP_PHASE_SEQUENCE {type: "NEXT_PHASE"}]->(p2),
       (p2)-[:TESTLAP_PHASE_SEQUENCE {type: "PREVIOUS_PHASE"}]->(p1);

MATCH (p2:TestlapPhase {id:2}), (p3:TestlapPhase {id:3})
CREATE (p2)-[:TESTLAP_PHASE_SEQUENCE {type: "NEXT_PHASE"}]->(p3),
       (p3)-[:TESTLAP_PHASE_SEQUENCE {type: "PREVIOUS_PHASE"}]->(p2);

MATCH (p3:TestlapPhase {id:3}), (p4:TestlapPhase {id:4})
CREATE (p3)-[:TESTLAP_PHASE_SEQUENCE {type: "NEXT_PHASE"}]->(p4),
       (p4)-[:TESTLAP_PHASE_SEQUENCE {type: "PREVIOUS_PHASE"}]->(p3);

MATCH (p4:TestlapPhase {id:4}), (p5:TestlapPhase {id:5})
CREATE (p4)-[:TESTLAP_PHASE_SEQUENCE {type: "NEXT_PHASE"}]->(p5),
       (p5)-[:TESTLAP_PHASE_SEQUENCE {type: "PREVIOUS_PHASE"}]->(p4);

MATCH (p5:TestlapPhase {id:5}), (p6:TestlapPhase {id:6})
CREATE (p5)-[:TESTLAP_PHASE_SEQUENCE {type: "NEXT_PHASE"}]->(p6),
       (p6)-[:TESTLAP_PHASE_SEQUENCE {type: "PREVIOUS_PHASE"}]->(p5);

MATCH (p6:TestlapPhase {id:6}), (p7:TestlapPhase {id:7})
CREATE (p6)-[:TESTLAP_PHASE_SEQUENCE {type: "NEXT_PHASE"}]->(p7),
       (p7)-[:TESTLAP_PHASE_SEQUENCE {type: "PREVIOUS_PHASE"}]->(p6);

// Create Instrument-Phase Relationships
MATCH (p:TestlapPhase), (i:TestlapInstrument)
WHERE p.id IN [1,2,3,4,5,6,7] AND i.id IN p.instrument_ids
CREATE (p)-[:TESTLAP_USES_INSTRUMENT]->(i);

// Create Synonym Relationships
MATCH (i1:TestlapInstrument {id:3}), (i2:TestlapInstrument {id:1})
CREATE (i1)-[:TESTLAP_SYNONYM_OF {relation: "Functional equivalent for blunt dissection"}]->(i2);

// Create Action Nodes with Instrument-Anatomy Links
CREATE (:TestlapAction {
  name: "Peritoneal Incision",
  description: "Electrosurgical opening of parietal peritoneum",
  phase: 2,
  instrument_id: 4,
  anatomy_id: 1,
  start_condition: "Visualization of uterosacral ligaments",
  end_condition: "Complete exposure of uterine artery bifurcation"
});

CREATE (:TestlapAction {
  name: "Vascular Pedicle Sealing",
  description: "Bipolar energy application to uterine artery complex",
  phase: 3,
  instrument_id: 2,
  anatomy_id: 1,
  start_condition: "Identification of ureteric course",
  end_condition: "Auditory feedback from LigaSure"
});

CREATE (:TestlapAction {
  name: "Colpotomy",
  description: "Circumferential vaginal transection",
  phase: 4,
  instrument_id: 4,
  anatomy_id: 1,
  start_condition: "Cervix elevated with manipulator",
  end_condition: "Complete separation from cervical stump"
});

// Link Actions to Phases
MATCH (a:TestlapAction), (p:TestlapPhase)
WHERE a.phase = p.id
CREATE (a)-[:TESTLAP_BELONGS_TO]->(p);

// Link Actions to Instruments
MATCH (a:TestlapAction), (i:TestlapInstrument)
WHERE a.instrument_id = i.id
CREATE (a)-[:TESTLAP_USES_INSTRUMENT]->(i);

// Link Actions to Anatomy
MATCH (a:TestlapAction), (an:TestlapAnatomy)
WHERE a.anatomy_id = an.id
CREATE (a)-[:TESTLAP_ACTS_ON]->(an); 