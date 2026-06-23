import { useEffect, useState } from 'react';

const defaultComponents = [
  { id: 1, name: 'Attendance', weight: 10, maxPoints: 100 },
  { id: 2, name: 'Assignment', weight: 10, maxPoints: 100 },
  { id: 3, name: 'Midterm Assignment', weight: 20, maxPoints: 100 },
  { id: 4, name: 'Final Assignment', weight: 40, maxPoints: 100 },
];

function toTitleCase(text) {
  return text
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

const CourseCreator = ({ course, onSave, onCancel }) => {
  const [courseName, setCourseName] = useState('');
  const [components, setComponents] = useState(defaultComponents);
  const [expectedTotal, setExpectedTotal] = useState(100);
  const [passingThreshold, setPassingThreshold] = useState(60);
  const [error, setError] = useState('');

  useEffect(() => {
    if (course) {
      setCourseName(course.name || '');
      setComponents(course.components || defaultComponents);
      setExpectedTotal(course.expectedTotal ?? 100);
      setPassingThreshold(course.passingThreshold ?? 60);
      setError('');
    } else {
      setCourseName('');
      setComponents(defaultComponents);
      setExpectedTotal(100);
      setPassingThreshold(60);
      setError('');
    }
  }, [course]);

  const totalWeight = components.reduce((sum, comp) => sum + Number(comp.weight || 0), 0);

  const updateComponent = (id, field, value) => {
    setComponents((prev) =>
      prev.map((comp) =>
        comp.id === id
          ? {
              ...comp,
              [field]: field === 'name' ? value : Number(value),
            }
          : comp
      )
    );
  };

  const addComponent = () => {
    setComponents((prev) => [
      ...prev,
      { id: Date.now(), name: 'New Component', weight: 0, maxPoints: 100 },
    ]);
  };

  const removeComponent = (id) => {
    setComponents((prev) => prev.filter((comp) => comp.id !== id));
  };

  const handleSubmit = () => {
    const trimmedName = courseName.trim();
    if (!trimmedName) {
      setError('Please enter a course name.');
      return;
    }
    if (totalWeight !== 100) {
      setError('Total percentage must be exactly 100%.');
      return;
    }
    if (expectedTotal <= 0 || expectedTotal > 100) {
      setError('Total performance expectation must be between 1 and 100.');
      return;
    }
    if (passingThreshold < 0 || passingThreshold > 100) {
      setError('Passing threshold must be between 0 and 100.');
      return;
    }

    const savedCourse = {
      id: course?.id,
      name: toTitleCase(trimmedName),
      components: components.map((comp) => ({
        ...comp,
        name: toTitleCase(comp.name || 'Untitled'),
      })),
      expectedTotal,
      passingThreshold,
    };
    onSave(savedCourse);
  };

  return (
    <div className="course-creator page-card">
      <div className="page-header">
        <div>
          <h2>{course ? 'Edit Course' : 'Create Course'}</h2>
          <p>Set up a course and adjust weights or max points.</p>
        </div>
        <button className="secondary" onClick={onCancel}>Back</button>
      </div>

      <div className="form-group">
        <label>Course Name</label>
        <input
          type="text"
          placeholder="Linear Algebra"
          value={courseName}
          onChange={(e) => setCourseName(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Total Performance Expectation (%)</label>
        <input
          type="number"
          min="1"
          max="100"
          value={expectedTotal}
          onChange={(e) => setExpectedTotal(Number(e.target.value))}
        />
      </div>

      <div className="form-group">
        <label>Passing Threshold (%)</label>
        <input
          type="number"
          min="0"
          max="100"
          value={passingThreshold}
          onChange={(e) => setPassingThreshold(Number(e.target.value))}
        />
      </div>

      <div className="component-table">
        <div className="table-row header">
          <div>Name</div>
          <div>Weight %</div>
          <div>Max Points</div>
          <div>Action</div>
        </div>
        {components.map((comp) => (
          <div key={comp.id} className="table-row">
            <input
              value={comp.name}
              onChange={(e) => updateComponent(comp.id, 'name', e.target.value)}
            />
            <input
              type="number"
              min="0"
              max="100"
              value={comp.weight}
              onChange={(e) => updateComponent(comp.id, 'weight', e.target.value)}
            />
            <input
              type="number"
              min="1"
              value={comp.maxPoints}
              onChange={(e) => updateComponent(comp.id, 'maxPoints', e.target.value)}
            />
            <button className="small" onClick={() => removeComponent(comp.id)}>
              Delete
            </button>
          </div>
        ))}
      </div>

      <div className="actions-row">
        <button className="secondary" onClick={addComponent}>+ Add Component</button>
        <div className="summary">
          <div>Total Performance Expectation: {expectedTotal}%</div>
          <div>Passing Threshold: {passingThreshold}%</div>
          <div>Total Weight: {totalWeight}%</div>
        </div>
      </div>

      {error && <div className="alert">{error}</div>}

      <button className="primary" onClick={handleSubmit} disabled={totalWeight !== 100}>
        {course ? 'Save Changes' : 'Create Course'}
      </button>
    </div>
  );
};

export default CourseCreator;
