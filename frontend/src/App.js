import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  LinearProgress,
  Drawer,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
  Chip,
  AppBar,
  Toolbar
} from '@mui/material';
import {
  CloudUpload,
  Analytics,
  BarChart,
  ShowChart,
  ScatterPlot,
  PieChart,
  Timeline,
  Chat as ChatIcon,
  Close as CloseIcon,
  Send as SendIcon
} from '@mui/icons-material';
import Plot from 'react-plotly.js';
import axios from 'axios';

const API_BASE = 'http://localhost:3001/api';
const DRAWER_WIDTH = 400;

function App() {
  const [dataset, setDataset] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [visualizations, setVisualizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [datasetName, setDatasetName] = useState('');
  const [chartData, setChartData] = useState({});
  const [activeTab, setActiveTab] = useState(0);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setDatasetName(file.name.split('.')[0]);
  };

  const processDataset = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setKpis(null);
    setVisualizations([]);
    setChartData({});

    try {
      console.log('Starting file upload...', selectedFile.name);
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('datasetName', datasetName);

      console.log('Sending request to:', `${API_BASE}/upload`);
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000 // 60 second timeout
      });

      console.log('Upload response received:', response.data);
      
      if (!response.data.success) {
        throw new Error('Upload failed: ' + (response.data.error || 'Unknown error'));
      }

      // Force state updates
      const datasetData = response.data.dataset;
      const kpisData = response.data.kpis || {};
      const vizData = response.data.visualizations || [];

      console.log('Setting state - Dataset:', datasetData?.name);
      console.log('Setting state - KPIs:', Object.keys(kpisData).length, 'items');
      console.log('Setting state - Visualizations:', vizData.length, 'items');
      console.log('Visualization details:', vizData.map(v => ({ type: v.type, title: v.title })));

      setDataset(datasetData);
      setKpis(kpisData);
      setVisualizations(vizData);
      
      // Force a re-render check
      console.log('State should be updated now');

      // Store dataset reference for chart data loading
      const datasetRef = response.data.dataset;
      const vizList = response.data.visualizations || [];

      // Load chart data for each visualization
      if (vizList.length > 0) {
        console.log('Loading chart data for', vizList.length, 'visualizations...');
        for (let i = 0; i < vizList.length; i++) {
          await loadChartData(vizList[i], datasetRef);
          // Small delay between requests
          if (i < vizList.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 200));
          }
        }
        console.log('All chart data loaded');
      }
    } catch (err) {
      console.error('Upload error:', err);
      const errorMsg = err.response?.data?.error || err.message || 'Failed to process file';
      setError(errorMsg);
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
    } finally {
      setLoading(false);
    }
  };

  const loadChartData = async (viz, datasetRef = dataset) => {
    if (!datasetRef) {
      console.warn('No dataset reference for chart data');
      return;
    }
    
    try {
      console.log('Loading chart data for:', viz.title, viz.type, viz.xColumn, viz.yColumn);
      const response = await axios.post(`${API_BASE}/chart-data`, {
        datasetName: datasetRef.name,
        chartType: viz.type,
        xColumn: viz.xColumn,
        yColumn: viz.yColumn || null
      });

      console.log('Chart data received:', viz.title, response.data);
      setChartData(prev => ({
        ...prev,
        [viz.title]: response.data
      }));
    } catch (err) {
      console.error('Error loading chart data:', err, err.response?.data);
      setChartData(prev => ({
        ...prev,
        [viz.title]: { error: err.response?.data?.error || 'Failed to load chart data' }
      }));
    }
  };

  const handleChatSend = async () => {
    if (!chatInput.trim() || !dataset) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: chatInput,
        datasetName: dataset.name,
        threadId: 'default'
      });

      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response || 'Analysis complete'
      }]);
    } catch (err) {
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.response?.data?.error || err.message}`
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const renderChart = (viz) => {
    const data = chartData[viz.title];
    
    if (!data) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress size={40} />
        </Box>
      );
    }

    if (data.error) {
      return (
        <Alert severity="error">
          {data.error}
        </Alert>
      );
    }

    if (!data.data) {
      return (
        <Alert severity="info">
          No data available for this chart
        </Alert>
      );
    }

    const layout = {
      title: viz.title,
      autosize: true,
      margin: { l: 60, r: 30, t: 60, b: 60 },
      paper_bgcolor: 'white',
      plot_bgcolor: '#f8f9fa',
      font: { family: 'Arial', size: 12 }
    };

    if (viz.type === 'heatmap' && data.data.z) {
      return (
        <Plot
          data={[{
            z: data.data.z,
            x: data.data.x,
            y: data.data.y,
            type: 'heatmap',
            colorscale: 'RdBu',
            showscale: true
          }]}
          layout={layout}
          style={{ width: '100%', height: '500px' }}
          config={{ displayModeBar: true, responsive: true }}
        />
      );
    }

    if (viz.type === 'histogram') {
      return (
        <Plot
          data={[{
            x: data.data.x || [],
            type: 'histogram',
            nbinsx: 30,
            marker: { color: '#4285f4' }
          }]}
          layout={layout}
          style={{ width: '100%', height: '500px' }}
          config={{ displayModeBar: true, responsive: true }}
        />
      );
    }

    const plotData = {
      x: data.data.x || [],
      y: data.data.y || [],
      type: data.data.type || 'bar',
      mode: data.data.mode || (viz.type === 'line' ? 'lines+markers' : 'markers'),
      marker: { 
        size: viz.type === 'scatter' ? 8 : undefined,
        color: '#4285f4'
      }
    };

    return (
      <Plot
        data={[plotData]}
        layout={layout}
        style={{ width: '100%', height: '500px' }}
        config={{ displayModeBar: true, responsive: true }}
      />
    );
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📊 Data Visualization Agent
          </Typography>
          {dataset && (
            <Button
              color="inherit"
              startIcon={<ChatIcon />}
              onClick={() => setChatOpen(true)}
            >
              Chat
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ flex: 1, pb: 4 }}>
        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Upload & Analyze Your Data
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Upload any data file and get instant KPIs and visualizations powered by AI
          </Typography>

          {/* File Upload Section */}
          <Box sx={{ my: 4, p: 3, border: '2px dashed #ccc', borderRadius: 2, bgcolor: '#fafafa' }}>
            <input
              accept=".csv,.json,.xlsx,.xls,.txt"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              onChange={handleFileUpload}
            />
            <label htmlFor="file-upload">
              <Button
                variant="contained"
                component="span"
                startIcon={<CloudUpload />}
                size="large"
                sx={{ mb: 2 }}
              >
                Choose File
              </Button>
            </label>
            {selectedFile && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  Selected: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(2)} KB)
                </Typography>
                <TextField
                  label="Dataset Name"
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                  fullWidth
                  sx={{ mb: 2 }}
                />
                <Button
                  variant="contained"
                  color="primary"
                  onClick={processDataset}
                  disabled={loading}
                  size="large"
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Analytics />}
                >
                  {loading ? 'Processing...' : '🚀 Load & Analyze Dataset'}
                </Button>
              </Box>
            )}
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* KPIs Section */}
          {kpis && Object.keys(kpis).length > 0 && (
            <Box sx={{ my: 4 }}>
              <Typography variant="h5" gutterBottom>
                📈 Key Performance Indicators
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                Found {Object.keys(kpis).length} KPI metric(s)
              </Alert>
              <Grid container spacing={2} sx={{ mt: 2 }}>
                {Object.entries(kpis).map(([metric, values]) => (
                  <Grid item xs={12} sm={6} md={3} key={metric}>
                    <Card sx={{ height: '100%' }}>
                      <CardContent>
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                          {metric.length > 30 ? metric.substring(0, 30) + '...' : metric}
                        </Typography>
                        {kpis[metric]?.display_name && (
                          <Typography variant="caption" color="text.secondary">
                            {kpis[metric].display_name}
                          </Typography>
                        )}
                        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
                          {values.mean?.toFixed(2) || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          Min: {values.min?.toFixed(2)} | Max: {values.max?.toFixed(2)}
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={100}
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Debug info */}
          {dataset && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Dataset loaded: {dataset.name} ({dataset.shape?.[0]} rows, {dataset.shape?.[1]} columns)
              {kpis && ` | KPIs: ${Object.keys(kpis).length}`}
              {visualizations && ` | Visualizations: ${visualizations.length}`}
            </Alert>
          )}

          {/* Visualizations Section */}
          {visualizations && visualizations.length > 0 ? (
            <Box sx={{ my: 4 }}>
              <Typography variant="h5" gutterBottom>
                📊 Generated Visualizations
              </Typography>
              <Alert severity="success" sx={{ mb: 2 }}>
                ✅ {visualizations.length} visualization(s) ready to view below!
                {Object.keys(chartData).length < visualizations.length && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Loading chart data... ({Object.keys(chartData).length}/{visualizations.length})
                  </Typography>
                )}
              </Alert>
              <Tabs
                value={activeTab}
                onChange={(e, newValue) => setActiveTab(newValue)}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
              >
                {visualizations.map((viz, idx) => (
                  <Tab
                    key={idx}
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {viz.type === 'histogram' && <BarChart fontSize="small" />}
                        {viz.type === 'bar' && <BarChart fontSize="small" />}
                        {viz.type === 'line' && <ShowChart fontSize="small" />}
                        {viz.type === 'scatter' && <ScatterPlot fontSize="small" />}
                        {viz.type === 'pie' && <PieChart fontSize="small" />}
                        {viz.type === 'heatmap' && <Timeline fontSize="small" />}
                        <span>{viz.title}</span>
                      </Box>
                    }
                  />
                ))}
              </Tabs>

              {visualizations.map((viz, idx) => (
                <Box
                  key={idx}
                  role="tabpanel"
                  hidden={activeTab !== idx}
                  sx={{ mt: 2 }}
                >
                  {activeTab === idx && (
                    <Paper sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        {viz.title}
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        {renderChart(viz)}
                      </Box>
                    </Paper>
                  )}
              </Box>
            ))}
          </Box>
          ) : dataset && (
            <Alert severity="warning" sx={{ my: 4 }}>
              No visualizations generated. Check console for details.
            </Alert>
          )}

          {!dataset && !loading && !error && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary">
                Upload a file to get started
              </Typography>
            </Box>
          )}

          {loading && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CircularProgress size={60} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                Processing your file...
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                This may take a few moments
              </Typography>
            </Box>
          )}
        </Paper>
      </Container>

      {/* Chat Drawer */}
      <Drawer
        anchor="right"
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">💬 Chat with AI Agent</Typography>
          <IconButton onClick={() => setChatOpen(false)}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider />
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {chatMessages.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
              Ask questions about your data...
            </Typography>
          ) : (
            <List>
              {chatMessages.map((msg, idx) => (
                <ListItem key={idx} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                  <Chip
                    label={msg.role === 'user' ? 'You' : 'AI'}
                    color={msg.role === 'user' ? 'primary' : 'default'}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                  <ListItemText
                    primary={msg.content}
                    sx={{ bgcolor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5', p: 1, borderRadius: 1 }}
                  />
                </ListItem>
              ))}
              {chatLoading && (
                <ListItem>
                  <CircularProgress size={20} />
                </ListItem>
              )}
            </List>
          )}
        </Box>
        <Divider />
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Ask about your data..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleChatSend();
                }
              }}
              disabled={chatLoading || !dataset}
            />
            <Button
              variant="contained"
              onClick={handleChatSend}
              disabled={chatLoading || !dataset || !chatInput.trim()}
              startIcon={<SendIcon />}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Drawer>
    </Box>
  );
}

export default App;
