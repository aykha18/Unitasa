import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';

interface ConfirmOptions {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'warning' | 'info';
}

interface ConfirmContextType {
  confirm: (options: ConfirmOptions) => Promise<boolean>;
}

const ConfirmContext = createContext<ConfirmContextType | undefined>(undefined);

export const useConfirm = () => {
  const context = useContext(ConfirmContext);
  if (!context) {
    throw new Error('useConfirm must be used within a ConfirmProvider');
  }
  return context;
};

export const ConfirmProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [options, setOptions] = useState<ConfirmOptions>({ message: '' });
  const [resolveRef, setResolveRef] = useState<((value: boolean) => void) | null>(null);

  const confirm = useCallback((opts: ConfirmOptions) => {
    setOptions(opts);
    setIsOpen(true);
    return new Promise<boolean>((resolve) => {
      setResolveRef(() => resolve);
    });
  }, []);

  const handleConfirm = () => {
    setIsOpen(false);
    if (resolveRef) {
      resolveRef(true);
      setResolveRef(null);
    }
  };

  const handleCancel = () => {
    setIsOpen(false);
    if (resolveRef) {
      resolveRef(false);
      setResolveRef(null);
    }
  };

  const getConfirmButtonVariant = () => {
    switch (options.type) {
      case 'danger':
        return 'danger'; // Assuming Button component has a 'danger' variant or similar
      case 'warning':
        return 'warning';
      default:
        return 'primary';
    }
  };

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      <Modal
        isOpen={isOpen}
        onClose={handleCancel}
        title={options.title || 'Confirm Action'}
        footer={
          <>
            <Button
              variant={options.type === 'danger' ? 'danger' : 'primary'} // Adjusted to match likely Button props, will check Button.tsx
              onClick={handleConfirm}
            >
              {options.confirmText || 'Confirm'}
            </Button>
            <Button variant="secondary" onClick={handleCancel}>
              {options.cancelText || 'Cancel'}
            </Button>
          </>
        }
      >
        <p className="text-gray-600">{options.message}</p>
      </Modal>
    </ConfirmContext.Provider>
  );
};
