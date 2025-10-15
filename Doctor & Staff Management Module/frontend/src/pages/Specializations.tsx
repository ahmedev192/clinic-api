import { motion } from 'framer-motion';
import { Heart, Baby, Bone, Syringe, Eye, Brain, Activity } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const mockSpecializations = [
  { id: 1, name: 'Cardiology', name_ar: 'أمراض القلب', icon: Heart, doctors: 3, color: 'text-destructive' },
  { id: 2, name: 'Pediatrics', name_ar: 'طب الأطفال', icon: Baby, doctors: 2, color: 'text-primary' },
  { id: 3, name: 'Orthopedics', name_ar: 'جراحة العظام', icon: Bone, doctors: 2, color: 'text-accent' },
  { id: 4, name: 'Dermatology', name_ar: 'الأمراض الجلدية', icon: Syringe, doctors: 2, color: 'text-success' },
  { id: 5, name: 'Ophthalmology', name_ar: 'طب العيون', icon: Eye, doctors: 1, color: 'text-warning' },
  { id: 6, name: 'Neurology', name_ar: 'طب الأعصاب', icon: Brain, doctors: 2, color: 'text-primary' },
  { id: 7, name: 'General Medicine', name_ar: 'الطب العام', icon: Activity, doctors: 1, color: 'text-accent' },
];

export default function Specializations() {
  const { t, language } = useLanguage();

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold mb-2">{t('specializations')}</h1>
        <p className="text-muted-foreground">Medical specializations available at the clinic</p>
      </motion.div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {mockSpecializations.map((spec, index) => (
          <motion.div
            key={spec.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.08 }}
            whileHover={{ scale: 1.02, boxShadow: 'var(--shadow-medium)' }}
          >
            <Card className="border-border/50 hover:border-primary/30 transition-all">
              <CardHeader>
                <div className="flex items-center gap-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-primary shadow-glow">
                    <spec.icon className="h-7 w-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-1">
                      {language === 'en' ? spec.name : spec.name_ar}
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {spec.doctors} {spec.doctors === 1 ? 'doctor' : 'doctors'}
                    </p>
                  </div>
                  <Badge>{spec.doctors}</Badge>
                </div>
              </CardHeader>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
