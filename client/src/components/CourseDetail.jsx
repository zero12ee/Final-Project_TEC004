import { useMemo, useState } from 'react';

/**
 * Utility function to calculate percentage
 * @param {number} value - Numerator
 * @param {number} total - Denominator
 * @returns {string} Percentage with 2 decimal places
 */
const percentageOf = (value, total) => (total > 0 ? ((value / total) * 100).toFixed(2) : '0.00');

/**
 * CourseDetail Component
 * 
 * Displays course components with score input fields and grade calculation
 * 
 * Features:
 * - Pre-populates component scores from CSV (if available)
 * - Tracks student input for each component
 * - Calculates weighted grades in real-time
 * - Suggests required scores to meet passing threshold
 * - Displays current total and passing status
 * 
 * Props:
 * - user: Current user object (for display)
 * - course: Course object with components array
 * - onBack: Callback to return to dashboard
 * 
 * Component Score Calculation:
 * - Input Score: Student's raw score for component
 * - Normalized: (Input Score / Max Points) * Weight
 * - Current Total: Sum of all normalized scores
 * - Passing: Current Total >= Passing Threshold
 */
const CourseDetail = ({ user, course, onBack }) => {
  // ================== STATE ==================
  
  /**
   * Component score inputs
   * Format: { [componentId]: scoreString }
   * 
   * Pre-populated with CSV scores if available
   * Empty string for unfilled/null scores
   */
  const [inputs, setInputs] = useState(() =>
    course.components.reduce((acc, comp) => {
      // Pre-populate with score from CSV if available, otherwise empty
      const value = comp.score !== null && comp.score !== undefined ? String(comp.score) : '';
      return { ...acc, [comp.id]: value };
    }, {})
  );

  /**
   * Calculation result from "Calculate" button
   * Format: {
   *   currentTotal: number,
   *   target: number (passing threshold),
   *   suggested: [{id, suggestedPoints, requiredPct}],
   *   isPassing: boolean
   * }
   */
  const [result, setResult] = useState(null);

  // ================== COMPUTED VALUES ==================
  
  // Calculate total weight from all components
  const totalWeight = course.components.reduce((sum, comp) => sum + Number(comp.weight), 0);

  // ================== HANDLERS ==================
  
  /**
   * Handle component score input change
   * @param {number} id - Component ID
   * @param {string} value - New score value
   */
  const handleInputChange = (id, value) => {
    setInputs((prev) => ({ ...prev, [id]: value }));
  };

  // ================== CALCULATED DATA ==================
  
  /**
   * Component list with calculated scores
   * Recalculates when course components or inputs change
   * 
   * For each component:
   * - inputScore: Parsed student input (null if empty)
   * - normalized: (inputScore / maxPoints) * weight
   *   (represents contribution to final grade)
   */
  const componentsWithScore = useMemo(() => {
    return course.components.map((comp) => {
      const inputScore = inputs[comp.id] !== '' ? Number(inputs[comp.id]) : null;
      const normalized = inputScore !== null ? (inputScore / comp.maxPoints) * comp.weight : null;
      return { ...comp, inputScore, normalized };
    });
  }, [course.components, inputs]);

  /**
   * Current total grade
   * Sum of all normalized component scores
   */
  const currentTotal = componentsWithScore.reduce(
    (sum, comp) => sum + (comp.normalized || 0),
    0
  );

  /**
   * Weight remaining for empty components
   * Used to determine if passing is still possible
   */
  const missingWeight = componentsWithScore.reduce(
    (sum, comp) => sum + (!comp.inputScore && comp.inputScore !== 0 ? comp.weight : 0),
    0
  );

  // ================== CALCULATE SUGGESTIONS ==================
  
  /**
   * Calculate suggested scores needed to reach passing threshold
   * 
   * Algorithm:
   * 1. Get passing threshold
   * 2. Find empty components
   * 3. Calculate how many points needed
   * 4. Distribute needed points proportionally by weight
   * 5. Suggest max(calculated, max_points) for each component
   */
  const handleCalculate = () => {
    // Use the course's configured passing threshold, defaulting to 60 if not set.
    const target = course.passingThreshold ?? 60;
    const missingComponents = componentsWithScore.filter((comp) => comp.inputScore === null);
    const filledTotal = currentTotal;
    const needed = Math.max(0, target - filledTotal);

    const suggested = missingComponents.map((comp) => {
      const share = missingComponents.length ? comp.weight / missingComponents.reduce((a, b) => a + b.weight, 0) : 0;
      const requiredPct = needed * share;
      const requiredPoints = Math.min(comp.maxPoints, Math.round((requiredPct / comp.weight) * comp.maxPoints));
      return { id: comp.id, suggestedPoints: requiredPoints, requiredPct: requiredPct.toFixed(2) };
    });

    setResult({
      currentTotal: filledTotal.toFixed(2),
      target,
      suggested,
      isPassing: filledTotal >= target,
    });
  };

  const displayName = user.username || String(user.id || 'User');

  return (
    <div className="container course-details">
      <div className="topbar">
        <span className="topbar-brand">Performance Tracker</span>
        <div className="topbar-user">
          <div className="avatar">{displayName.charAt(0).toUpperCase()}</div>
          <span>{displayName}</span>
          <button type="button" className="btn-logout" onClick={onBack}>Back</button>
        </div>
      </div>

      <div className="course-header">
        <div>
          <h2>Course: {course.name}</h2>
          <p>Student: {user.id}</p>
        </div>
      </div>

      <div className="components-grid">
        {componentsWithScore.map((comp) => (
          <div key={comp.id} className="component-card">
            <div className="component-card-header">
              <h4>{comp.name}</h4>
              <span className="component-weight">{comp.weight}%</span>
            </div>
            <div className="component-card-body">
              <div className="input-group">
                <label>Your points</label>
                <input
                  type="number"
                  min="0"
                  max={comp.maxPoints}
                  value={comp.inputScore ?? ''}
                  onChange={(e) => handleInputChange(comp.id, e.target.value)}
                  placeholder="Enter points"
                />
              </div>
              <div className="component-card-stats">
                <div className="stat">
                  <span className="stat-value">{comp.inputScore !== null ? comp.inputScore : '-'}</span>
                  <span className="stat-label">/ {comp.maxPoints}</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{comp.normalized !== null ? comp.normalized.toFixed(2) : '-'}</span>
                  <span className="stat-label">/ {comp.weight}%</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="summary-box">
        <div>
          <strong>Total Expectation</strong>
          <p>{course.expectedTotal ?? 100}%</p>
        </div>
        <div>
          <strong>Current Total</strong>
          <p>{currentTotal.toFixed(2)}%</p>
        </div>
        <div>
          <strong>Passing Threshold</strong>
          <p>{course.passingThreshold ?? 60}%</p>
        </div>
      </div>

      <button className="primary" onClick={handleCalculate}>Calculate</button>

      {result && (
        <div className={`result-card ${result.isPassing ? 'safe' : 'risk'}`}>
          <h3>{result.isPassing ? 'On Track to Pass' : 'Not Pass'}</h3>
          <p>Current Percentage: {result.currentTotal}%</p>
          <p>Target: {result.target}%</p>
          <div>
            <h4>Suggested Points for Missing Components</h4>
            <ul>
              {result.suggested.map((item) => {
                const component = course.components.find((comp) => comp.id === item.id);
                return (
                  <li key={item.id}>
                    {component.name}: {item.suggestedPoints} points ({item.requiredPct}% of component weight)
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseDetail;
