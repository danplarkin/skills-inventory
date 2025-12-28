// Skills Inventory Dashboard Application

// Sample data (in production, this would come from API/S3)
const sampleData = {
    totalSkills: 45,
    totalClusters: 5,
    totalEmployees: 20,
    avgProficiency: 3.2,
    clusters: [
        { id: 0, name: "Programming Languages", skills: ["Python", "JavaScript", "Java", "Go"], count: 12 },
        { id: 1, name: "Cloud & DevOps", skills: ["AWS", "Docker", "Kubernetes", "CI/CD"], count: 8 },
        { id: 2, name: "Data & Analytics", skills: ["SQL", "Machine Learning", "Statistics", "Tableau"], count: 10 },
        { id: 3, name: "Business Skills", skills: ["Salesforce", "CRM", "Product Management", "Agile"], count: 9 },
        { id: 4, name: "Creative & Marketing", skills: ["SEO", "Content Marketing", "UI/UX Design", "Figma"], count: 6 }
    ],
    gaps: [
        { skill: "Blockchain", required: 5, current: 0, gap: 5, priority: "High" },
        { skill: "AI/ML Engineering", required: 8, current: 3, gap: 5, priority: "High" },
        { skill: "Cloud Security", required: 6, current: 2, gap: 4, priority: "Medium" },
        { skill: "Mobile Development", required: 7, current: 4, gap: 3, priority: "Medium" },
        { skill: "DevSecOps", required: 5, current: 3, gap: 2, priority: "Low" }
    ]
};

// Initialize dashboard
function initDashboard() {
    updateMetrics();
    renderClusterVisualization();
    renderGapAnalysis();
    setupEventListeners();
}

// Update dashboard metrics
function updateMetrics() {
    document.getElementById('total-skills').textContent = sampleData.totalSkills;
    document.getElementById('total-clusters').textContent = sampleData.totalClusters;
    document.getElementById('total-employees').textContent = sampleData.totalEmployees;
    document.getElementById('avg-proficiency').textContent = sampleData.avgProficiency.toFixed(1);
}

// Render cluster visualization using D3
function renderClusterVisualization() {
    const container = document.getElementById('cluster-chart');
    const width = container.offsetWidth;
    const height = 500;

    const svg = d3.select('#cluster-chart')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Prepare data for bubble chart
    const bubbleData = sampleData.clusters.map(cluster => ({
        name: cluster.name,
        value: cluster.count,
        skills: cluster.skills.join(', ')
    }));

    // Create pack layout
    const pack = d3.pack()
        .size([width - 50, height - 50])
        .padding(20);

    const root = d3.hierarchy({ children: bubbleData })
        .sum(d => d.value);

    const nodes = pack(root).leaves();

    // Color scale
    const color = d3.scaleOrdinal()
        .domain(bubbleData.map(d => d.name))
        .range(['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']);

    // Create bubbles
    const bubble = svg.selectAll('.bubble')
        .data(nodes)
        .enter()
        .append('g')
        .attr('class', 'bubble')
        .attr('transform', d => `translate(${d.x + 25},${d.y + 25})`);

    bubble.append('circle')
        .attr('r', d => d.r)
        .attr('fill', d => color(d.data.name))
        .attr('opacity', 0.7)
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

    bubble.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '-0.5em')
        .style('font-size', d => `${Math.min(d.r / 4, 16)}px`)
        .style('font-weight', 'bold')
        .style('fill', '#fff')
        .text(d => d.data.name);

    bubble.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.8em')
        .style('font-size', d => `${Math.min(d.r / 5, 14)}px`)
        .style('fill', '#fff')
        .text(d => `${d.data.value} skills`);

    // Add tooltip
    bubble.append('title')
        .text(d => `${d.data.name}\nSkills: ${d.data.skills}\nCount: ${d.data.value}`);
}

// Render gap analysis table
function renderGapAnalysis() {
    const container = document.getElementById('gap-table');
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Skill</th>
                    <th>Required</th>
                    <th>Current</th>
                    <th>Gap</th>
                    <th>Priority</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;

    sampleData.gaps.forEach(gap => {
        const priorityColor = gap.priority === 'High' ? '#e74c3c' : 
                             gap.priority === 'Medium' ? '#f39c12' : '#27ae60';
        
        html += `
            <tr>
                <td><strong>${gap.skill}</strong></td>
                <td>${gap.required}</td>
                <td>${gap.current}</td>
                <td><strong>${gap.gap}</strong></td>
                <td><span style="color: ${priorityColor}; font-weight: bold;">${gap.priority}</span></td>
                <td><button onclick="alert('Hire or train for ${gap.skill}')">Take Action</button></td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('department-filter').addEventListener('change', (e) => {
        console.log('Filter changed to:', e.target.value);
        // In production, this would fetch filtered data
    });

    document.getElementById('export-btn').addEventListener('click', () => {
        exportToCSV();
    });
}

// Export data to CSV
function exportToCSV() {
    let csv = 'Skill,Required,Current,Gap,Priority\n';
    
    sampleData.gaps.forEach(gap => {
        csv += `${gap.skill},${gap.required},${gap.current},${gap.gap},${gap.priority}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'skills_gap_analysis.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initDashboard);
