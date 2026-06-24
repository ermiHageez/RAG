import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00c853', light: '#69f0ae', dark: '#009624', contrastText: '#000000' },
    secondary: { main: '#2979ff', light: '#5393ff', dark: '#1c54b2' },
    success: { main: '#00c853' },
    warning: { main: '#ff9100' },
    error: { main: '#ff1744' },
    info: { main: '#2979ff' },
    background: { default: '#121214', paper: '#1a1a1e' },
    text: { primary: '#e8eaed', secondary: '#9aa0a6' },
    divider: 'rgba(255,255,255,0.08)',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 600, letterSpacing: '-0.02em' },
    h5: { fontWeight: 600, letterSpacing: '-0.01em' },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    subtitle2: { fontWeight: 500 },
    body2: { color: '#9aa0a6' },
    caption: { color: '#9aa0a6' },
  },
  shape: { borderRadius: 6 },
  components: {
    MuiCssBaseline: {
      styleOverrides: { body: { backgroundColor: '#121214' } },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', fontWeight: 500, borderRadius: 6,
          border: '1px solid rgba(255,255,255,0.08)',
        },
        containedPrimary: {
          border: '1px solid rgba(0,200,83,0.3)',
          '&:hover': { border: '1px solid rgba(0,200,83,0.5)' },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(255,255,255,0.08)',
          boxShadow: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
        outlined: { border: '1px solid rgba(255,255,255,0.08)' },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          boxShadow: 'none',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 4 },
        outlined: { border: '1px solid rgba(255,255,255,0.12)' },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
            '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
          },
        },
      },
    },
    MuiDivider: { styleOverrides: { root: { borderColor: 'rgba(255,255,255,0.08)' } } },
  },
})
