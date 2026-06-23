import { useState } from 'react';

const CourseCreator = ({ onSave }) => {
    const [courseName, setCourseName] = useState('');
    const [components, setComponents] = useState([
        { id: 1, name: 'Attendance', weight: 10, max_points: 100 },
        { id: 2, name: 'Assignment', weight: 10, max_points: 100 },
        { id: 3, name: 'Midterm', weight: 20, max_points: 100 },
        { id: 4, name: 'Final', weight: 40, max_points: 100 },
        { id: 5, name: 'Participation', weight: 10, max_points: 100 },
        { id: 6, name: 'Other', weight: 10, max_points: 100 },
    ]);

    // Calculate total weight dynamically
    const totalWeight = components.reduce((sum, comp) => sum + Number(comp.weight), 0);

    const updateComponent = (id, field, value) => {
        setComponents(components.map(c => c.id === id ? { ...c, [field]: value } : c));
    };

    const addComponent = () => {
        setComponents([...components, { id: Date.now(), name: 'New Component', weight: 0, max_points: 100 }]);
    };

    const removeComponent = (id) => {
        setComponents(components.filter(c => c.id !== id));
    };

    const handleSubmit = () => {
        if (totalWeight !== 100) {
            alert(`Error: Total percentage must be 100%. Currently: ${totalWeight}%`);
            return;
        }
        if (!courseName) {
            alert("Please enter a course name.");
            return;
        }
        onSave({ courseName, components });
    };

    return (
        <div className="course-creator">
            <h2>Create New Course</h2>
            <input 
                placeholder="Course Name (e.g. Linear Algebra)" 
                value={courseName}
                onChange={(e) => setCourseName(e.target.value)}
            />
            
            <div className="component-list">
                {components.map((comp) => (
                    <div key={comp.id} className="comp-row">
                        <input value={comp.name} onChange={(e) => updateComponent(comp.id, 'name', e.target.value)} />
                        <input type="number" value={comp.weight} onChange={(e) => updateComponent(comp.id, 'weight', e.target.value)} />
                        <input type="number" value={comp.max_points} onChange={(e) => updateComponent(comp.id, 'max_points', e.target.value)} />
                        <button onClick={() => removeComponent(comp.id)}>Delete</button>
                    </div>
                ))}
            </div>

            <button onClick={addComponent}>+ Add Component</button>
            <p><strong>Total Weight: {totalWeight}%</strong></p>
            <button onClick={handleSubmit} disabled={totalWeight !== 100}>Create Course</button>
        </div>
    );
};

export default CourseCreator;

import axios from 'axios';

export default function CourseView({ course }) {
    const [inputs, setInputs] = useState({});
    const [result, setResult] = useState(null);

    const handleCalculate = async () => {
        const payload = course.components.map(c => ({...c, input_points: inputs[c.id]}));
        const res = await axios.post('http://localhost:5000/api/predict', { components: payload });
        setResult(res.data);
    };

    return (
        <div>
            <h3>Course: {course.name}</h3>
            {course.components.map(c => (
                <div key={c.id}>
                    <label>{c.name} ({c.weight}%)</label>
                    <input type="number" onChange={(e) => setInputs({...inputs, [c.id]: e.target.value})} />
                </div>
            ))}
            <button onClick={handleCalculate}>Calculate & Predict</button>
            {result && (
                <div style={{color: result.is_passing ? 'green' : 'red'}}>
                    Total: {result.current_total}% | Suggested for missing: {result.suggested_score_needed}%
                </div>
            )}
        </div>
    );
}