import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Calendar, Shield, Star, Clock } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

// Mock data
const mockDoctors = [
  {
    id: 1,
    name: 'Dr. Ahmed Hassan',
    name_ar: 'د. أحمد حسن',
    specialization: 'Cardiology',
    experience: 15,
    fee: '$150',
    hours: '9:00 AM - 5:00 PM',
    available: true,
    rating: 4.8,
  },
  {
    id: 2,
    name: 'Dr. Fatima Ali',
    name_ar: 'د. فاطمة علي',
    specialization: 'Pediatrics',
    experience: 10,
    fee: '$120',
    hours: '10:00 AM - 6:00 PM',
    available: true,
    rating: 4.9,
  },
  {
    id: 3,
    name: 'Dr. Omar Khan',
    name_ar: 'د. عمر خان',
    specialization: 'Orthopedics',
    experience: 12,
    fee: '$140',
    hours: '8:00 AM - 4:00 PM',
    available: false,
    rating: 4.7,
  },
  {
    id: 4,
    name: 'Dr. Layla Ibrahim',
    name_ar: 'د. ليلى إبراهيم',
    specialization: 'Dermatology',
    experience: 8,
    fee: '$130',
    hours: '11:00 AM - 7:00 PM',
    available: true,
    rating: 4.6,
  },
];

export default function Doctors() {
  const { t, language } = useLanguage();

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('doctors')}</h1>
          <p className="text-muted-foreground">Manage doctor profiles and availability</p>
        </div>
        
        <Button className="bg-gradient-primary text-white shadow-glow hover:opacity-90">
          <Plus className="h-4 w-4 mr-2" />
          {t('add_new')}
        </Button>
      </motion.div>

      {/* Doctor Cards Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {mockDoctors.map((doctor, index) => (
          <motion.div
            key={doctor.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1, duration: 0.3 }}
            whileHover={{ y: -8, boxShadow: 'var(--shadow-large)' }}
          >
            <Card className="overflow-hidden border-border/50 hover:border-primary/30 transition-all">
              <div className="h-2 bg-gradient-primary" />
              
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-primary text-white text-2xl font-bold shadow-glow">
                      {doctor.name.split(' ')[1].charAt(0)}
                    </div>
                    <div>
                      <CardTitle className="text-lg mb-1">
                        {language === 'en' ? doctor.name : doctor.name_ar}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">{doctor.specialization}</p>
                      <div className="flex items-center gap-1 mt-1">
                        <Star className="h-4 w-4 fill-warning text-warning" />
                        <span className="text-sm font-medium">{doctor.rating}</span>
                      </div>
                    </div>
                  </div>
                  <Badge variant={doctor.available ? 'default' : 'secondary'}>
                    {doctor.available ? 'Available' : 'Busy'}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2 text-sm">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/20">
                      <Shield className="h-4 w-4 text-accent" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">{t('experience')}</p>
                      <p className="font-semibold">{doctor.experience} {t('years')}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-success/20">
                      <Clock className="h-4 w-4 text-success" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Fee</p>
                      <p className="font-semibold">{doctor.fee}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-3 rounded-lg bg-muted/50">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm">{doctor.hours}</p>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" className="flex-1" size="sm">
                    <Calendar className="h-4 w-4 mr-2" />
                    {t('view_schedule')}
                  </Button>
                  <Button variant="outline" className="flex-1" size="sm">
                    <Shield className="h-4 w-4 mr-2" />
                    {t('assign_role')}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
