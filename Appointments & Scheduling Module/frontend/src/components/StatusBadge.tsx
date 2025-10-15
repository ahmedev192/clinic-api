import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { useLanguage } from '@/contexts/LanguageContext';

export type AppointmentStatus = 'scheduled' | 'completed' | 'cancelled' | 'no-show' | 'confirmed';

interface StatusBadgeProps {
  status: AppointmentStatus;
  className?: string;
}

const statusConfig = {
  scheduled: {
    en: 'Scheduled',
    ar: 'مجدول',
    variant: 'default' as const,
  },
  confirmed: {
    en: 'Confirmed',
    ar: 'مؤكد',
    variant: 'default' as const,
  },
  completed: {
    en: 'Completed',
    ar: 'مكتمل',
    variant: 'default' as const,
  },
  cancelled: {
    en: 'Cancelled',
    ar: 'ملغى',
    variant: 'destructive' as const,
  },
  'no-show': {
    en: 'No Show',
    ar: 'لم يحضر',
    variant: 'destructive' as const,
  },
};

export const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  const { t } = useLanguage();
  const config = statusConfig[status] || statusConfig.scheduled;

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <Badge variant={config.variant} className={className}>
        {t(status, { en: config.en, ar: config.ar })}
      </Badge>
    </motion.div>
  );
};
