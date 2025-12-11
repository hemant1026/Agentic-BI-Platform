const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Configure multer for file uploads
const upload = multer({ 
    dest: 'uploads/',
    limits: { fileSize: 50 * 1024 * 1024 } // 50MB limit
});

// Ensure uploads directory exists
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

// Import Python script runner
const { spawn } = require('child_process');

// Store for datasets (in production, use a database)
const datasets = new Map();
const visualizations = new Map();
const kpis = new Map();

// Helper function to run Python scripts
function runPythonScript(scriptPath, args = []) {
    return new Promise((resolve, reject) => {
        const python = spawn('python3', [scriptPath, ...args]);
        let output = '';
        let error = '';

        python.stdout.on('data', (data) => {
            output += data.toString();
        });

        python.stderr.on('data', (data) => {
            // Log stderr but don't treat as error (debug messages)
            const stderrMsg = data.toString();
            console.log('Python stderr:', stderrMsg.trim());
            error += stderrMsg;
        });

        python.on('close', (code) => {
            if (code === 0) {
                try {
                    const parsed = JSON.parse(output);
                    // Check if the parsed result has an error field
                    if (parsed.error) {
                        reject(new Error(parsed.error));
                    } else {
                        resolve(parsed);
                    }
                } catch (e) {
                    // If output is not JSON, check if it's an error message
                    if (output.trim().startsWith('{') && output.includes('error')) {
                        try {
                            const parsed = JSON.parse(output);
                            if (parsed.error) {
                                reject(new Error(parsed.error));
                            } else {
                                resolve({ output, raw: true });
                            }
                        } catch (e2) {
                            resolve({ output, raw: true });
                        }
                    } else {
                        resolve({ output, raw: true });
                    }
                }
            } else {
                // Try to parse error output as JSON to get the actual error message
                let errorMessage = error || `Process exited with code ${code}`;
                try {
                    if (output.trim().startsWith('{')) {
                        const parsed = JSON.parse(output);
                        if (parsed.error) {
                            errorMessage = parsed.error;
                        }
                    }
                } catch (e) {
                    // Use the original error message
                }
                reject(new Error(errorMessage));
            }
        });
    });
}

// Upload and process dataset
app.post('/api/upload', upload.single('file'), async (req, res) => {
    try {
        console.log('Upload request received');
        if (!req.file) {
            console.error('No file in request');
            return res.status(400).json({ error: 'No file uploaded' });
        }

        const filePath = req.file.path;
        const fileName = req.file.originalname;
        const datasetName = req.body.datasetName || fileName.split('.')[0];

        console.log(`Processing file: ${fileName} as dataset: ${datasetName}`);

        // Process file with Python using BI Agent Team for deep analysis
        const processScript = path.join(__dirname, 'bi_agent_team.py');
        const absoluteFilePath = path.resolve(filePath);
        console.log(`Running BI Agent Team analysis: ${processScript} with file: ${absoluteFilePath}`);
        
        let result = await runPythonScript(processScript, [absoluteFilePath]);
        
        // If BI agent team fails, fall back to basic processing
        if (result.error) {
            console.log('BI Agent Team failed, falling back to basic processing');
            const basicScript = path.join(__dirname, 'process_data.py');
            result = await runPythonScript(basicScript, [absoluteFilePath, datasetName]);
        }
        
        console.log('Python script completed, result keys:', Object.keys(result));
        
        if (result.error) {
            console.error('Python script error:', result.error);
            throw new Error(result.error);
        }
        
        if (result.raw && result.output) {
            // If we got raw output, try to parse it
            try {
                const parsed = JSON.parse(result.output);
                Object.assign(result, parsed);
                console.log('Parsed raw output, result keys:', Object.keys(result));
            } catch (e) {
                console.log('Could not parse raw output, using as-is');
                // If parsing fails, result might already be parsed
            }
        }

        // Store dataset info
        datasets.set(datasetName, {
            name: datasetName,
            filePath: filePath,
            originalName: fileName,
            data: result.data,
            columns: result.columns,
            shape: result.shape,
            numericColumns: result.numericColumns,
            categoricalColumns: result.categoricalColumns
        });

        // Use KPIs and visualizations from BI agent team if available
        let kpiResult = result.kpis || generateKPIs(result.data, result.numericColumns);
        let vizResult = result.visualizations || generateVisualizations(datasetName, result);
        
        // Ensure all visualizations have datasetName and enhance KPI names
        vizResult = vizResult.map(viz => {
            if (!viz.datasetName) {
                viz.datasetName = datasetName;
            }
            return viz;
        });
        
        // Enhance KPI names with display names from metadata
        if (result.column_metadata && result.column_metadata.length > 0) {
            const metadataMap = {};
            result.column_metadata.forEach(meta => {
                // Map both clean and original names
                const key = meta.clean || meta.original;
                metadataMap[key] = meta;
                if (meta.original && meta.original !== key) {
                    metadataMap[meta.original] = meta;
                }
            });
            
            const enhancedKPIs = {};
            Object.keys(kpiResult).forEach(key => {
                const meta = metadataMap[key];
                if (meta && meta.display_name) {
                    // Use display name as the key
                    enhancedKPIs[meta.display_name] = {
                        ...kpiResult[key],
                        original_key: key,
                        description: meta.description || ''
                    };
                } else {
                    // Try to find a better name by checking if key matches any column
                    let found = false;
                    for (const [metaKey, metaValue] of Object.entries(metadataMap)) {
                        if (metaKey === key || metaValue.clean === key || metaValue.original === key) {
                            if (metaValue.display_name) {
                                enhancedKPIs[metaValue.display_name] = {
                                    ...kpiResult[key],
                                    original_key: key,
                                    description: metaValue.description || ''
                                };
                                found = true;
                                break;
                            }
                        }
                    }
                    if (!found) {
                        // Keep original but try to clean it up
                        const cleanedKey = key.replace(/^Column[_ ]?/i, '').replace(/^Value[_ ]?/i, '');
                        enhancedKPIs[cleanedKey || key] = {
                            ...kpiResult[key],
                            original_key: key
                        };
                    }
                }
            });
            kpiResult = enhancedKPIs;
        }
        
        kpis.set(datasetName, kpiResult);
        visualizations.set(datasetName, vizResult);

        console.log(`Generated ${Object.keys(kpiResult).length} KPIs and ${vizResult.length} visualizations`);

        const responseData = {
            success: true,
            dataset: {
                name: datasetName,
                shape: result.shape,
                columns: result.columns,
                numericColumns: result.numericColumns,
                categoricalColumns: result.categoricalColumns
            },
            kpis: kpiResult,
            visualizations: vizResult
        };

        console.log('Sending response with', vizResult.length, 'visualizations');
        res.json(responseData);
    } catch (error) {
        console.error('Upload error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Generate KPIs
function generateKPIs(data, numericColumns) {
    const kpis = {};
    
    numericColumns.forEach(col => {
        const values = data.map(row => parseFloat(row[col])).filter(v => !isNaN(v));
        if (values.length > 0) {
            kpis[col] = {
                mean: values.reduce((a, b) => a + b, 0) / values.length,
                median: values.sort((a, b) => a - b)[Math.floor(values.length / 2)],
                min: Math.min(...values),
                max: Math.max(...values),
                std: calculateStdDev(values),
                count: values.length,
                sum: values.reduce((a, b) => a + b, 0)
            };
        }
    });
    
    return kpis;
}

function calculateStdDev(values) {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const squareDiffs = values.map(value => Math.pow(value - mean, 2));
    const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / values.length;
    return Math.sqrt(avgSquareDiff);
}

// Generate visualizations
function generateVisualizations(datasetName, dataInfo) {
    const visualizations = [];
    const { numericColumns, categoricalColumns, data } = dataInfo;

    // Histograms for numeric columns
    numericColumns.slice(0, 2).forEach(col => {
        visualizations.push({
            type: 'histogram',
            title: `Distribution of ${col}`,
            xColumn: col,
            yColumn: null,
            datasetName: datasetName
        });
    });

    // Bar charts for categorical columns
    categoricalColumns.slice(0, 2).forEach(col => {
        const uniqueValues = new Set(data.map(row => row[col])).size;
        if (uniqueValues <= 20) {
            visualizations.push({
                type: 'bar',
                title: `Frequency of ${col}`,
                xColumn: col,
                yColumn: null,
                datasetName: datasetName
            });
        }
    });

    // Scatter plot
    if (numericColumns.length >= 2) {
        visualizations.push({
            type: 'scatter',
            title: `${numericColumns[0]} vs ${numericColumns[1]}`,
            xColumn: numericColumns[0],
            yColumn: numericColumns[1],
            datasetName: datasetName
        });
    }

    // Line chart if date column exists
    const dateColumns = dataInfo.columns.filter(col => 
        col.toLowerCase().includes('date') || col.toLowerCase().includes('time')
    );
    if (dateColumns.length > 0 && numericColumns.length > 0) {
        visualizations.push({
            type: 'line',
            title: `${numericColumns[0]} Over Time`,
            xColumn: dateColumns[0],
            yColumn: numericColumns[0],
            datasetName: datasetName
        });
    }

    // Heatmap
    if (numericColumns.length >= 3) {
        visualizations.push({
            type: 'heatmap',
            title: 'Correlation Matrix',
            xColumn: null,
            yColumn: null,
            datasetName: datasetName,
            columns: numericColumns.slice(0, 5)
        });
    }

    return visualizations;
}

// Get dataset data
app.get('/api/dataset/:name', (req, res) => {
    const dataset = datasets.get(req.params.name);
    if (!dataset) {
        return res.status(404).json({ error: 'Dataset not found' });
    }
    res.json(dataset);
});

// Get visualizations
app.get('/api/visualizations/:datasetName', (req, res) => {
    const viz = visualizations.get(req.params.datasetName);
    if (!viz) {
        return res.status(404).json({ error: 'Visualizations not found' });
    }
    res.json(viz);
});

// Get KPIs
app.get('/api/kpis/:datasetName', (req, res) => {
    const kpi = kpis.get(req.params.datasetName);
    if (!kpi) {
        return res.status(404).json({ error: 'KPIs not found' });
    }
    res.json(kpi);
});

// Get chart data - use stored data instead of re-reading file
app.post('/api/chart-data', async (req, res) => {
    try {
        const { datasetName, chartType, xColumn, yColumn } = req.body;
        const dataset = datasets.get(datasetName);
        
        if (!dataset) {
            return res.status(404).json({ error: 'Dataset not found' });
        }

        // Use stored data instead of re-reading file to ensure column names match
        const data = dataset.data;
        const columns = dataset.columns;
        
        // Generate chart data directly from stored data
        const result = {
            chartType: chartType,
            xColumn: xColumn,
            yColumn: yColumn || null
        };

        try {
            if (chartType === 'histogram' && xColumn && columns.includes(xColumn)) {
                const values = data.map(row => parseFloat(row[xColumn])).filter(v => !isNaN(v));
                if (values.length > 0) {
                    result.data = { x: values, type: 'histogram' };
                } else {
                    result.error = `Column ${xColumn} has no numeric data`;
                }
            } else if (chartType === 'bar' && xColumn && columns.includes(xColumn)) {
                if (yColumn && columns.includes(yColumn)) {
                    // Bar chart with x and y
                    const xData = data.map(row => row[xColumn]).filter(v => v != null);
                    const yData = data.map(row => parseFloat(row[yColumn])).filter(v => !isNaN(v));
                    if (xData.length > 0 && yData.length > 0) {
                        result.data = {
                            x: xData.slice(0, Math.min(xData.length, yData.length)),
                            y: yData.slice(0, Math.min(xData.length, yData.length)),
                            type: 'bar'
                        };
                    } else {
                        result.error = 'No valid data for bar chart';
                    }
                } else {
                    // Frequency bar chart
                    const values = data.map(row => row[xColumn]).filter(v => v != null && v !== '');
                    if (values.length > 0) {
                        const counts = {};
                        values.forEach(v => {
                            const key = String(v);
                            counts[key] = (counts[key] || 0) + 1;
                        });
                        const sorted = Object.entries(counts)
                            .sort((a, b) => b[1] - a[1])
                            .slice(0, 20);
                        result.data = {
                            x: sorted.map(([k]) => k),
                            y: sorted.map(([, v]) => v),
                            type: 'bar'
                        };
                    } else {
                        result.error = `Column ${xColumn} has no data`;
                    }
                }
            } else if (chartType === 'scatter' && xColumn && yColumn && columns.includes(xColumn) && columns.includes(yColumn)) {
                const xData = data.map(row => parseFloat(row[xColumn])).filter(v => !isNaN(v));
                const yData = data.map(row => parseFloat(row[yColumn])).filter(v => !isNaN(v));
                const minLen = Math.min(xData.length, yData.length);
                if (minLen > 0) {
                    result.data = {
                        x: xData.slice(0, minLen),
                        y: yData.slice(0, minLen),
                        type: 'scatter',
                        mode: 'markers'
                    };
                } else {
                    result.error = 'No valid numeric data for scatter plot';
                }
            } else if (chartType === 'line' && xColumn && yColumn && columns.includes(xColumn) && columns.includes(yColumn)) {
                const pairs = data
                    .map(row => ({
                        x: row[xColumn],
                        y: parseFloat(row[yColumn])
                    }))
                    .filter(p => p.x != null && !isNaN(p.y))
                    .sort((a, b) => String(a.x).localeCompare(String(b.x)));
                if (pairs.length > 0) {
                    result.data = {
                        x: pairs.map(p => p.x),
                        y: pairs.map(p => p.y),
                        type: 'scatter',
                        mode: 'lines+markers'
                    };
                } else {
                    result.error = 'No valid data for line chart';
                }
            } else if (chartType === 'heatmap') {
                // Calculate correlation matrix for numeric columns
                const numericCols = dataset.numericColumns || [];
                if (numericCols.length > 1) {
                    // Simple correlation calculation
                    const corrData = [];
                    const colNames = numericCols.slice(0, 5);
                    for (let i = 0; i < colNames.length; i++) {
                        const row = [];
                        for (let j = 0; j < colNames.length; j++) {
                            const col1 = colNames[i];
                            const col2 = colNames[j];
                            const vals1 = data.map(r => parseFloat(r[col1])).filter(v => !isNaN(v));
                            const vals2 = data.map(r => parseFloat(r[col2])).filter(v => !isNaN(v));
                            const minLen = Math.min(vals1.length, vals2.length);
                            if (minLen > 0) {
                                const mean1 = vals1.slice(0, minLen).reduce((a, b) => a + b, 0) / minLen;
                                const mean2 = vals2.slice(0, minLen).reduce((a, b) => a + b, 0) / minLen;
                                let numerator = 0, denom1 = 0, denom2 = 0;
                                for (let k = 0; k < minLen; k++) {
                                    const diff1 = vals1[k] - mean1;
                                    const diff2 = vals2[k] - mean2;
                                    numerator += diff1 * diff2;
                                    denom1 += diff1 * diff1;
                                    denom2 += diff2 * diff2;
                                }
                                const corr = denom1 > 0 && denom2 > 0 ? numerator / Math.sqrt(denom1 * denom2) : 0;
                                row.push(corr);
                            } else {
                                row.push(0);
                            }
                        }
                        corrData.push(row);
                    }
                    result.data = {
                        z: corrData,
                        x: colNames,
                        y: colNames,
                        type: 'heatmap'
                    };
                } else {
                    result.error = 'Not enough numeric columns for heatmap';
                }
            } else {
                result.error = `Could not generate chart data. Column ${xColumn} not found in columns: ${columns.slice(0, 5).join(', ')}`;
            }
        } catch (error) {
            result.error = error.message;
        }

        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Chat with agent
app.post('/api/chat', async (req, res) => {
    try {
        const { message, datasetName, threadId } = req.body;
        
        // Call Python agent
        const chatScript = path.join(__dirname, 'chat_agent.py');
        const result = await runPythonScript(chatScript, [
            message,
            datasetName || '',
            threadId || 'default'
        ]);

        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// List all datasets
app.get('/api/datasets', (req, res) => {
    const datasetList = Array.from(datasets.values()).map(d => ({
        name: d.name,
        shape: d.shape,
        columns: d.columns.length
    }));
    res.json(datasetList);
});

app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});

