import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, FileText, Plus } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import apiService from '@/services/api';
import { toast } from 'sonner';

export default function MedicalHistory() {
  const { t } = useLanguage();
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = async () => {
    try {
      setLoading(true);
      // In real scenario, you'd filter by patient
      const data = await apiService.getMedicalHistory('all');
      setRecords(data.results || data || []);
    } catch (error) {
      console.error('Failed to load medical history:', error);
      // Mock data for development
      setRecords([
        {
          id: '1',
          date: '2024-01-15',
          diagnosis: 'Common Cold',
          treatment: 'Rest and hydration, Paracetamol 500mg',
          notes: 'Patient shows signs of improvement',
          patient_name: 'John Doe',
        },
        {
          id: '2',
          date: '2023-12-20',
          diagnosis: 'Annual Checkup',
          treatment: 'No treatment required',
          notes: 'All vitals normal',
          patient_name: 'John Doe',
        },
        {
          id: '3',
          date: '2023-11-10',
          diagnosis: 'Hypertension',
          treatment: 'Lifestyle modifications, Amlodipine 5mg daily',
          notes: 'Follow up in 3 months',
          patient_name: 'Jane Smith',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-hero p-8 text-white shadow-large flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('medical-history')}</h1>
          <p className="text-white/90">View and manage patient medical history</p>
        </div>
        <Button className="bg-white text-primary hover:bg-white/90 shadow-glow">
          <Plus className="h-4 w-4 mr-2" />
          {t('add-history')}
        </Button>
      </motion.div>

      {/* Timeline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="relative"
      >
        {loading ? (
          <Card className="shadow-soft">
            <CardContent className="p-8">
              <p className="text-center text-muted-foreground">{t('loading')}</p>
            </CardContent>
          </Card>
        ) : records.length === 0 ? (
          <Card className="shadow-soft">
            <CardContent className="p-8">
              <p className="text-center text-muted-foreground">No medical history records</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Timeline line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border hidden md:block" />

            {records.map((record, index) => (
              <motion.div
                key={record.id}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                className="relative"
              >
                {/* Timeline dot */}
                <div className="absolute left-6 w-5 h-5 rounded-full bg-primary border-4 border-background shadow-glow hidden md:block" />

                <Card className="md:ml-20 shadow-soft hover:shadow-medium transition-all">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <Calendar className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <h3 className="font-bold text-lg">{record.diagnosis}</h3>
                          <p className="text-sm text-muted-foreground">
                            {record.patient_name} • {record.date}
                          </p>
                        </div>
                      </div>
                      <Badge variant="outline">{record.date}</Badge>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <p className="text-sm font-semibold text-muted-foreground mb-1">
                          {t('treatment')}
                        </p>
                        <p className="text-sm">{record.treatment}</p>
                      </div>

                      {record.notes && (
                        <div>
                          <p className="text-sm font-semibold text-muted-foreground mb-1">
                            {t('notes')}
                          </p>
                          <p className="text-sm text-muted-foreground">{record.notes}</p>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
                      <Button variant="ghost" size="sm">
                        <FileText className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
