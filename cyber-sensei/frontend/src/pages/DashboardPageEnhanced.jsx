import React, { useState, useEffect } from 'react';
import './DashboardPage.css';

/**
 * Enhanced Dashboard with personalized recommendations and progress tracking.
 * Features:
 * - User progress visualization
 * - Personalized topic recommendations
 * - Learning streak and statistics
 * - Quick access to modules
 */
const DashboardPage = ({ userId }) => {
  const [modules, setModules] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [userProgress, setUserProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCompleted: 0,
    avgScore: 0,
    streak: 0,
    timeSpent: 0
  });

  // Fetch data on component mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        // Fetch modules
        const modulesRes = await fetch('/api/modules');
        const modulesData = await modulesRes.json();
        setModules(modulesData);

        // Fetch user progress
        const progressRes = await fetch('/api/progress', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const progressData = await progressRes.json();
        setUserProgress(progressData);

        // Fetch recommendations
        const recsRes = await fetch(`/api/recommendations/${userId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const recsData = await recsRes.json();
        setRecommendations(recsData.recommendations || []);

        // Calculate statistics
        if (progressData.length > 0) {
          const totalCompleted = progressData.filter(p => p.completion_percentage >= 95).length;
          const avgScore = (progressData.reduce((sum, p) => sum + p.completion_percentage, 0) / progressData.length).toFixed(1);

          setStats({
            totalCompleted,
            avgScore,
            streak: calculateStreak(progressData),
            timeSpent: calculateTimeSpent(progressData)
          });
        }

        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [userId]);

  const calculateStreak = (progress) => {
    // Simple streak calculation based on recent progress
    return progress.filter(p => 
      new Date(p.last_accessed) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    ).length;
  };

  const calculateTimeSpent = (progress) => {
    // Estimate based on completion percentage (simplified)
    return progress.reduce((sum, p) => sum + (p.completion_percentage * 10), 0);
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 90) return '#27ae60'; // Green
    if (percentage >= 70) return '#f39c12'; // Orange
    if (percentage >= 50) return '#e74c3c'; // Red
    return '#95a5a6'; // Gray
  };

  if (loading) {
    return <div className="dashboard-loading">Loading your learning dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Your Learning Dashboard</h1>
        <p>Stay on track with your cybersecurity learning journey</p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <StatCard
          title="Topics Completed"
          value={stats.totalCompleted}
          icon="✅"
          color="#27ae60"
        />
        <StatCard
          title="Average Progress"
          value={`${stats.avgScore}%`}
          icon="📊"
          color="#3498db"
        />
        <StatCard
          title="Learning Streak"
          value={stats.streak}
          subtext="days"
          icon="🔥"
          color="#e74c3c"
        />
        <StatCard
          title="Hours Learning"
          value={Math.round(stats.timeSpent / 60)}
          subtext="hours"
          icon="⏱️"
          color="#9b59b6"
        />
      </div>

      <div className="dashboard-content">
        {/* Recommendations Section */}
        <section className="recommendations-section">
          <h2>Recommended For You</h2>
          <div className="recommendations-grid">
            {recommendations.length > 0 ? (
              recommendations.map((rec, index) => (
                <div key={index} className="recommendation-card">
                  <div className="rec-header">
                    <h3>Topic ID: {rec.topic_id}</h3>
                    <span className="rec-score">{(rec.score * 100).toFixed(0)}%</span>
                  </div>
                  <p className="rec-reason">{rec.reason}</p>
                  <button className="btn-start-learning">Start Learning</button>
                </div>
              ))
            ) : (
              <p className="no-recommendations">Recommendations will appear as you progress</p>
            )}
          </div>
        </section>

        {/* Progress Section */}
        <section className="progress-section">
          <h2>Your Progress</h2>
          <div className="progress-list">
            {userProgress.map((prog) => (
              <div key={prog.id} className="progress-item">
                <div className="progress-info">
                  <h4>Topic {prog.topic_id}</h4>
                  <span className="last-accessed">
                    Last accessed: {new Date(prog.last_accessed).toLocaleDateString()}
                  </span>
                </div>
                <div className="progress-bar-container">
                  <div
                    className="progress-bar"
                    style={{
                      width: `${prog.completion_percentage}%`,
                      backgroundColor: getProgressColor(prog.completion_percentage)
                    }}
                  />
                </div>
                <span className="progress-percentage">{prog.completion_percentage}%</span>
              </div>
            ))}
          </div>
        </section>

        {/* Modules Section */}
        <section className="modules-section">
          <h2>Learning Modules</h2>
          <div className="modules-grid">
            {modules.map((module) => (
              <ModuleCard
                key={module.id}
                module={module}
                progress={userProgress.find(p => p.topic_id === module.id)?.completion_percentage || 0}
              />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

/**
 * StatCard Component - Display individual statistic
 */
const StatCard = ({ title, value, subtext, icon, color }) => (
  <div className="stat-card" style={{ borderLeftColor: color }}>
    <span className="stat-icon">{icon}</span>
    <div className="stat-content">
      <p className="stat-title">{title}</p>
      <h3 className="stat-value">{value}</h3>
      {subtext && <p className="stat-subtext">{subtext}</p>}
    </div>
  </div>
);

/**
 * ModuleCard Component - Display learning module with progress
 */
const ModuleCard = ({ module, progress }) => (
  <div className="module-card">
    <div className="module-icon">{module.icon || '📚'}</div>
    <h3>{module.name}</h3>
    <p className="module-desc">{module.description.substring(0, 80)}...</p>
    <div className="module-progress">
      <div className="progress-bar-small">
        <div
          className="progress-bar-fill"
          style={{ width: `${progress}%` }}
        />
      </div>
      <span className="progress-text">{progress}%</span>
    </div>
    <button className="btn-continue">Continue Learning →</button>
  </div>
);

export default DashboardPage;
