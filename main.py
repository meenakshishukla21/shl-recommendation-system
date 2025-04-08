from flask import Flask, render_template, request, jsonify

# Create a Flask app instance
app = Flask(__name__)

# Hardcoded SHL-like catalogue (replace with real data from SHL)
catalogue = [
    {
        "name": "Verify G+",
        "type": "Cognitive Ability",
        "job_family": ["General"],
        "skills": ["Numerical Reasoning", "Deductive Reasoning", "Inductive Reasoning"],
        "industry": "All",
        "level": "All",
        "description": "Measures general cognitive ability for all job types."
    },
    {
        "name": "OPQ32",
        "type": "Personality",
        "job_family": ["Management", "Leadership"],
        "skills": ["Leadership", "Teamwork", "Decision Making"],
        "industry": "All",
        "level": "Mid-Senior",
        "description": "Assesses personality traits for leadership and management roles."
    },
    {
        "name": "Coding Simulation",
        "type": "Skills",
        "job_family": ["IT", "Technical"],
        "skills": ["Programming", "Problem Solving"],
        "industry": "Tech",
        "level": "Entry-Mid",
        "description": "Evaluates coding skills for technical roles."
    },
    {
        "name": "Customer Contact Simulation",
        "type": "Job Simulation",
        "job_family": ["Customer Service"],
        "skills": ["Communication", "Multitasking"],
        "industry": ["Retail", "Call Centers"],
        "level": "Entry",
        "description": "Simulates customer service scenarios."
    }
]

# Similarity calculation for matching inputs to catalogue
def calculate_similarity(input_value, catalogue_value, weight):
    if isinstance(catalogue_value, list):
        if input_value.lower() in [v.lower() for v in catalogue_value]:
            return weight
        return weight * 0.5  # Partial match
    if input_value.lower() == catalogue_value.lower() or catalogue_value == "All":
        return weight
    return 0

# Recommendation engine logic
def recommend_assessments(input_data, catalogue):
    recommendations = []
    for assessment in catalogue:
        score = 0
        # Job role (40%)
        score += calculate_similarity(input_data["job_role"], assessment["job_family"], 40)
        # Industry (20%)
        score += calculate_similarity(input_data["industry"], assessment["industry"], 20)
        # Skills (30%)
        skill_match = sum(1 for skill in input_data["skills"] if skill in assessment["skills"]) / len(input_data["skills"])
        score += 30 * skill_match
        # Level (10%)
        score += calculate_similarity(input_data["level"], assessment["level"], 10)
        # Penalty for mismatch
        if input_data["level"] == "Entry" and "Senior" in assessment["level"]:
            score -= 20
        recommendations.append({
            "name": assessment["name"],
            "score": min(100, max(0, score)),
            "type": assessment["type"],
            "description": assessment["description"]
        })
    
    # Sort by score and return top 3
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:3]

# Flask routes
@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = None
    if request.method == "POST":
        # Collect form data
        user_input = {
            "job_role": request.form["job_role"],
            "industry": request.form["industry"],
            "skills": [skill.strip() for skill in request.form["skills"].split(",")],
            "level": request.form["level"],
            "purpose": "Hiring"  # Hardcoded for simplicity; could be a form field
        }
        # Get recommendations
        recommendations = recommend_assessments(user_input, catalogue)
    
    return render_template('index.html', recommendations=recommendations)

# New GET API endpoint returning JSON
@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    try:
        # Collect query parameters from the GET request
        job_role = request.args.get("job_role")
        industry = request.args.get("industry")
        skills = request.args.get("skills")  # Expecting comma-separated skills
        level = request.args.get("level")

        # Validate required parameters
        if not all([job_role, industry, skills, level]):
            return jsonify({"error": "Missing required parameters: job_role, industry, skills, level"}), 400

        # Prepare input data
        user_input = {
            "job_role": job_role,
            "industry": industry,
            "skills": [skill.strip() for skill in skills.split(",")],
            "level": level,
            "purpose": "Hiring"  # Hardcoded for simplicity
        }

        # Get recommendations
        recommendations = recommend_assessments(user_input, catalogue)

        # Return JSON response
        return jsonify({
            "status": "success",
            "recommendations": recommendations
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)