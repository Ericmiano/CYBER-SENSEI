import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, TextField, InputAdornment, IconButton, Paper,
  List, ListItem, ListItemIcon, ListItemText, CircularProgress,
  Typography, Divider, Chip
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  BookOpen as BookIcon,
  School as SchoolIcon,
  FileDocument as DocIcon
} from '@mui/icons-material';

const SearchBar = ({ onSearch, onNavigate }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      setOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        // Simulate API call - replace with actual API
        const mockResults = [
          {
            id: 1,
            type: 'topic',
            title: `Topic: ${query}`,
            description: 'Learning topic',
            icon: 'school'
          },
          {
            id: 2,
            type: 'document',
            title: `Document: ${query}`,
            description: 'Knowledge base article',
            icon: 'doc'
          },
          {
            id: 3,
            type: 'course',
            title: `Course: ${query}`,
            description: 'Learning course',
            icon: 'book'
          }
        ].filter(item =>
          item.title.toLowerCase().includes(query.toLowerCase())
        );

        setResults(mockResults);
        setOpen(mockResults.length > 0);
        setActiveIndex(-1);
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300); // Debounce 300ms

    return () => clearTimeout(timer);
  }, [query]);

  const getIcon = (iconType) => {
    switch (iconType) {
      case 'school':
        return <SchoolIcon sx={{ color: '#7c4dff' }} />;
      case 'doc':
        return <DocIcon sx={{ color: '#00acc1' }} />;
      case 'book':
        return <BookIcon sx={{ color: '#4caf50' }} />;
      default:
        return <SearchIcon />;
    }
  };

  const handleSelect = (item) => {
    if (onSearch) {
      onSearch(item);
    }
    if (onNavigate) {
      onNavigate(`/${item.type}/${item.id}`);
    }
    setQuery('');
    setOpen(false);
  };

  const handleKeyDown = (e) => {
    if (!open) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex(prev =>
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(prev => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (activeIndex >= 0 && results[activeIndex]) {
          handleSelect(results[activeIndex]);
        }
        break;
      case 'Escape':
        setOpen(false);
        break;
      default:
        break;
    }
  };

  return (
    <Box sx={{ position: 'relative', width: '100%', maxWidth: '400px' }}>
      <TextField
        fullWidth
        placeholder="Search topics, documents..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => query.length >= 2 && setOpen(true)}
        size="small"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon sx={{ color: '#00acc1' }} />
            </InputAdornment>
          ),
          endAdornment: query && (
            <InputAdornment position="end">
              <IconButton
                size="small"
                onClick={() => {
                  setQuery('');
                  setResults([]);
                  setOpen(false);
                }}
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            backgroundColor: '#f5f5f5',
            borderRadius: '20px',
            '&:hover': {
              backgroundColor: '#efefef'
            }
          }
        }}
      />

      {/* Search Results Dropdown */}
      {open && (
        <Paper
          sx={{
            position: 'absolute',
            top: 'calc(100% + 8px)',
            left: 0,
            right: 0,
            zIndex: 1000,
            maxHeight: '400px',
            overflowY: 'auto',
            boxShadow: '0 8px 24px rgba(0,0,0,0.15)'
          }}
        >
          {loading ? (
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
              <CircularProgress size={24} />
            </Box>
          ) : results.length > 0 ? (
            <>
              <List sx={{ p: 0 }}>
                {results.map((item, idx) => (
                  <React.Fragment key={item.id}>
                    <ListItem
                      button
                      selected={activeIndex === idx}
                      onClick={() => handleSelect(item)}
                      onMouseEnter={() => setActiveIndex(idx)}
                      sx={{
                        backgroundColor:
                          activeIndex === idx ? '#f5f5f5' : 'transparent',
                        transition: 'background-color 0.2s',
                        '&:hover': {
                          backgroundColor: '#f5f5f5'
                        }
                      }}
                    >
                      <ListItemIcon>
                        {getIcon(item.icon)}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.title}
                        secondary={item.description}
                        primaryTypographyProps={{
                          variant: 'body2',
                          sx={{ fontWeight: 500 }
                        }}
                        secondaryTypographyProps={{
                          variant: 'caption'
                        }}
                      />
                      <Chip
                        label={item.type}
                        size="small"
                        variant="outlined"
                        sx={{ ml: 1 }}
                      />
                    </ListItem>
                    {idx < results.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              <Divider />
              <Box sx={{ p: 1, textAlign: 'center' }}>
                <Typography variant="caption" color="textSecondary">
                  Found {results.length} result{results.length !== 1 ? 's' : ''}
                </Typography>
              </Box>
            </>
          ) : (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="textSecondary">
                No results found for "{query}"
              </Typography>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default SearchBar;
