import React, { useState } from 'react';
import { 
  Button, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Typography, 
  Box,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { Info as InfoIcon } from '@mui/icons-material';

const PrivacyDisclaimer: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const openModal = () => setIsOpen(true);
  const closeModal = () => setIsOpen(false);

  return (
    <>
      {/* Disclaimer Button */}
      <Button
        variant="outlined"
        color="info"
        startIcon={<InfoIcon />}
        onClick={openModal}
        size="small"
        sx={{ 
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 2
        }}
      >
        Privacy Disclaimer
      </Button>

      {/* Modal Dialog */}
      <Dialog
        open={isOpen}
        onClose={closeModal}
        maxWidth="md"
        fullWidth
        scroll="paper"
        PaperProps={{
          sx: {
            borderRadius: 2,
            maxHeight: '90vh'
          }
        }}
      >
        <DialogTitle sx={{ 
          bgcolor: 'primary.main', 
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <InfoIcon />
          Privacy Disclaimer
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Your Privacy is Our Priority
            </Typography>
            
            <Typography variant="body1" paragraph>
              <strong>No Data Storage or Collection:</strong> This application does not store, save, or collect any of your personal information, financial data, or personally identifiable information (PII). All calculations and processing are performed locally within your browser or device.
            </Typography>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              What This Means:
            </Typography>
            
            <List dense>
              <ListItem sx={{ pl: 0 }}>
                <ListItemText 
                  primary="• Your tax information never leaves your device"
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
              <ListItem sx={{ pl: 0 }}>
                <ListItemText 
                  primary="• No personal data is transmitted to external servers"
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
              <ListItem sx={{ pl: 0 }}>
                <ListItemText 
                  primary="• No financial information is stored in databases or cloud services"
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
              <ListItem sx={{ pl: 0 }}>
                <ListItemText 
                  primary="• No tracking, analytics, or user profiling is performed"
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
              <ListItem sx={{ pl: 0 }}>
                <ListItemText 
                  primary="• No cookies or local storage containing personal information are created"
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            </List>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Local Processing Only:
            </Typography>
            <Typography variant="body2" paragraph>
              All tax calculations, form completions, and data processing occur entirely on your local device. The application functions as a calculator tool without any backend data collection or storage mechanisms.
            </Typography>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              No Third-Party Sharing:
            </Typography>
            <Typography variant="body2" paragraph>
              Since no data is collected, there is nothing to share with third parties, government agencies, or other organizations.
            </Typography>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Your Responsibility:
            </Typography>
            <Typography variant="body2" paragraph>
              You are responsible for saving, printing, or backing up any tax documents or calculations you wish to retain. We recommend saving your work locally and securely deleting any sensitive files when no longer needed.
            </Typography>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ 
            bgcolor: 'warning.light', 
            p: 2, 
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'warning.main'
          }}>
            <Typography variant="h6" color="warning.dark" gutterBottom>
              Disclaimer:
            </Typography>
            <Typography variant="body2" color="warning.dark">
              This application is provided for informational and calculation purposes only. It is not a substitute for professional tax advice. Always consult with a qualified tax professional or refer to official Canada Revenue Agency guidelines for your specific tax situation.
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button 
            onClick={closeModal} 
            variant="contained" 
            color="primary"
            sx={{ textTransform: 'none' }}
          >
            I Understand
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default PrivacyDisclaimer;
