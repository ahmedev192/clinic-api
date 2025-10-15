import { motion } from 'framer-motion';
import { useLanguage } from '@/contexts/LanguageContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const hours = ['9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'];

const mockSchedules = {
  'Dr. Ahmed Hassan': [
    { day: 'Monday', start: '9:00', end: '13:00' },
    { day: 'Wednesday', start: '9:00', end: '13:00' },
    { day: 'Friday', start: '14:00', end: '17:00' },
  ],
  'Dr. Fatima Ali': [
    { day: 'Tuesday', start: '10:00', end: '14:00' },
    { day: 'Thursday', start: '10:00', end: '14:00' },
  ],
};

export default function Schedules() {
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold mb-2">{t('schedules')}</h1>
        <p className="text-muted-foreground">Manage doctor schedules and availability</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid gap-6"
      >
        {Object.entries(mockSchedules).map(([doctor, schedule], index) => (
          <Card key={doctor} className="hover:shadow-medium transition-all">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{doctor}</span>
                <Badge>{schedule.length} sessions</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {schedule.map((slot, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="flex items-center gap-4 p-4 rounded-lg bg-gradient-card border border-border/50"
                  >
                    <div className="flex-1">
                      <p className="font-semibold">{slot.day}</p>
                      <p className="text-sm text-muted-foreground">
                        {slot.start} - {slot.end}
                      </p>
                    </div>
                    <Badge variant="outline">{parseInt(slot.end.split(':')[0]) - parseInt(slot.start.split(':')[0])}h</Badge>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>
    </div>
  );
}
