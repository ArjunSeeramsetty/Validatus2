/**
 * Pergola Analysis Chat Interface
 * Segment-specific chat with RAG-powered responses
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Collapse,
  Card,
  CardContent,
  Avatar,
  Divider
} from '@mui/material';
import {
  Send,
  Person,
  SmartToy,
  ExpandMore,
  ExpandLess,
  Source
} from '@mui/icons-material';

interface ChatMessage {
  id: string;
  message: string;
  response: string;
  sources: Array<{
    id: string;
    source: string;
    snippet: string;
    metadata: any;
  }>;
  timestamp: string;
  segment: string;
}

interface PergolaChat {
  segment: string;
  onSegmentChange?: (segment: string) => void;
}

const PergolaChat: React.FC<PergolaChat> = ({ segment, onSegmentChange }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedSources, setExpandedSources] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const availableSegments = [
    { id: 'general', name: 'General', color: '#1890ff' },
    { id: 'consumer', name: 'Consumer', color: '#52c41a' },
    { id: 'market', name: 'Market', color: '#fa8c16' },
    { id: 'product', name: 'Product', color: '#722ed1' },
    { id: 'brand', name: 'Brand', color: '#eb2f96' },
    { id: 'business_case', name: 'Business Case', color: '#13c2c2' },
    { id: 'experience', name: 'Experience', color: '#f5222d' }
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || loading) return;

    const userMessage = currentMessage;
    setCurrentMessage('');
    setLoading(true);

    try {
      const baseUrl = window.location.origin;
      const response = await fetch(`${baseUrl}/api/v3/chat/pergola`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          segment,
          conversation_history: messages.slice(-6) // Last 6 messages for context
        })
      });

      const chatResponse = await response.json();
      
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        message: userMessage,
        response: chatResponse.response,
        sources: chatResponse.sources,
        timestamp: chatResponse.timestamp,
        segment: chatResponse.segment
      };

      setMessages(prev => [...prev, newMessage]);
      
    } catch (error) {
      console.error('Chat error:', error);
      // Add error message
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        message: userMessage,
        response: 'Sorry, I encountered an error processing your request. Please try again.',
        sources: [],
        timestamp: new Date().toISOString(),
        segment
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getCurrentSegmentColor = () => {
    return availableSegments.find(s => s.id === segment)?.color || '#1890ff';
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Segment Selector */}
      <Box sx={{ p: 2, borderBottom: '1px solid #3d3d56' }}>
        <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
          Analysis Segment
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {availableSegments.map((seg) => (
            <Chip
              key={seg.id}
              label={seg.name}
              onClick={() => onSegmentChange?.(seg.id)}
              sx={{
                backgroundColor: seg.id === segment ? `${seg.color}20` : '#3d3d56',
                color: seg.id === segment ? seg.color : '#b8b8cc',
                border: seg.id === segment ? `1px solid ${seg.color}` : 'none',
                '&:hover': {
                  backgroundColor: `${seg.color}30`
                }
              }}
            />
          ))}
        </Box>
      </Box>

      {/* Messages */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {messages.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <SmartToy sx={{ fontSize: 48, color: getCurrentSegmentColor(), mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 1 }}>
              Pergola Analysis Assistant
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              Ask me anything about the LAMARK pergola business case analysis.
              I have access to comprehensive market research, competitive analysis, and strategic insights.
            </Typography>
          </Box>
        )}

        {messages.map((msg) => (
          <Box key={msg.id} sx={{ mb: 3 }}>
            {/* User Message */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', maxWidth: '80%' }}>
                <Paper sx={{ 
                  p: 2, 
                  backgroundColor: getCurrentSegmentColor(),
                  color: 'white',
                  mr: 1
                }}>
                  <Typography variant="body2">{msg.message}</Typography>
                </Paper>
                <Avatar sx={{ bgcolor: getCurrentSegmentColor() }}>
                  <Person />
                </Avatar>
              </Box>
            </Box>

            {/* AI Response */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', maxWidth: '80%' }}>
                <Avatar sx={{ bgcolor: '#252547', mr: 1 }}>
                  <SmartToy />
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Paper sx={{ 
                    p: 2, 
                    backgroundColor: '#252547',
                    border: '1px solid #3d3d56'
                  }}>
                    <Typography variant="body2" sx={{ color: '#e8e8f0', whiteSpace: 'pre-wrap' }}>
                      {msg.response}
                    </Typography>
                    
                    {msg.sources.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            cursor: 'pointer',
                            '&:hover': { color: getCurrentSegmentColor() }
                          }}
                          onClick={() => setExpandedSources(
                            expandedSources === msg.id ? null : msg.id
                          )}
                        >
                          <Source sx={{ fontSize: 16, mr: 1, color: '#b8b8cc' }} />
                          <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                            {msg.sources.length} sources
                          </Typography>
                          {expandedSources === msg.id ? 
                            <ExpandLess sx={{ fontSize: 16, ml: 1 }} /> :
                            <ExpandMore sx={{ fontSize: 16, ml: 1 }} />
                          }
                        </Box>
                        
                        <Collapse in={expandedSources === msg.id}>
                          <Box sx={{ mt: 1 }}>
                            {msg.sources.map((source, idx) => (
                              <Card key={idx} sx={{ 
                                backgroundColor: '#1a1a35', 
                                mb: 1,
                                border: '1px solid #3d3d56'
                              }}>
                                <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                                  <Typography variant="caption" sx={{ color: getCurrentSegmentColor() }}>
                                    {source.source}
                                  </Typography>
                                  <Typography variant="body2" sx={{ color: '#b8b8cc', fontSize: '0.75rem' }}>
                                    {source.snippet}
                                  </Typography>
                                </CardContent>
                              </Card>
                            ))}
                          </Box>
                        </Collapse>
                      </Box>
                    )}
                  </Paper>
                </Box>
              </Box>
            </Box>
          </Box>
        ))}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box sx={{ p: 2, borderTop: '1px solid #3d3d56' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder={`Ask about ${availableSegments.find(s => s.id === segment)?.name.toLowerCase()} analysis...`}
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#252547',
                '& fieldset': { borderColor: '#3d3d56' },
                '&:hover fieldset': { borderColor: getCurrentSegmentColor() },
                '&.Mui-focused fieldset': { borderColor: getCurrentSegmentColor() }
              },
              '& .MuiInputBase-input': { color: '#e8e8f0' }
            }}
          />
          <IconButton
            onClick={handleSendMessage}
            disabled={!currentMessage.trim() || loading}
            sx={{
              backgroundColor: getCurrentSegmentColor(),
              color: 'white',
              '&:hover': {
                backgroundColor: getCurrentSegmentColor(),
                opacity: 0.8
              },
              '&.Mui-disabled': {
                backgroundColor: '#3d3d56',
                color: '#666'
              }
            }}
          >
            <Send />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default PergolaChat;
