import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, FileText, AlertCircle, Heart, Edit } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import apiService from '@/services/api';
import { toast } from 'sonner';

export default function PatientProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [patient, setPatient] = useState<any>(null);
  const [medicalHistory, setMedicalHistory] = useState<any[]>([]);
  const [allergies, setAllergies] = useState<any[]>([]);
  const [chronicConditions, setChronicConditions] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadPatientData();
    }
  }, [id]);

  const loadPatientData = async () => {
    try {
      setLoading(true);
      const [patientData, historyData, allergiesData, conditionsData, documentsData] =
        await Promise.all([
          apiService.getPatient(id!),
          apiService.getMedicalHistory(id!),
          apiService.getAllergies(id!),
          apiService.getChronicConditions(id!),
          apiService.getDocuments(id!),
        ]);

      setPatient(patientData);
      setMedicalHistory(historyData.results || historyData || []);
      setAllergies(allergiesData.results || allergiesData || []);
      setChronicConditions(conditionsData.results || conditionsData || []);
      setDocuments(documentsData.results || documentsData || []);
    } catch (error) {
      toast.error(t('error-occurred'));
      console.error('Failed to load patient data:', error);
      // Mock data for development
      setPatient({
        id,
        first_name_en: 'John',
        last_name_en: 'Doe',
        phone_primary: '+1234567890',
        email: 'john.doe@email.com',
        date_of_birth: '1990-05-15',
        gender: 'M',
        national_id: '1234567890',
        blood_type: 'A+',
        city: 'New York',
        address: '123 Main St',
        is_active: true,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-muted-foreground">{t('loading')}</div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">{t('no-patients')}</p>
      </div>
    );
  }

  const calculateAge = (dob: string) => {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/patients')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">
              {patient.first_name_en} {patient.last_name_en}
            </h1>
            <p className="text-muted-foreground">
              {t('patient-details')} • {calculateAge(patient.date_of_birth)} {t('years-old')}
            </p>
          </div>
        </div>
        <Button onClick={() => navigate(`/patients/${id}/edit`)}>
          <Edit className="h-4 w-4 mr-2" />
          {t('edit')}
        </Button>
      </motion.div>

      {/* Status Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-2xl bg-gradient-hero p-6 text-white shadow-large"
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <p className="text-white/70 text-sm">{t('phone')}</p>
            <p className="font-semibold">{patient.phone_primary}</p>
          </div>
          <div>
            <p className="text-white/70 text-sm">{t('email')}</p>
            <p className="font-semibold">{patient.email || 'N/A'}</p>
          </div>
          <div>
            <p className="text-white/70 text-sm">{t('blood-type')}</p>
            <p className="font-semibold">{patient.blood_type || 'N/A'}</p>
          </div>
          <div>
            <p className="text-white/70 text-sm">{t('status')}</p>
            <Badge
              className={patient.is_active ? 'bg-success' : 'bg-warning'}
            >
              {patient.is_active ? t('active') : t('inactive')}
            </Badge>
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Tabs defaultValue="personal" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto">
            <TabsTrigger value="personal">
              <User className="h-4 w-4 mr-2" />
              {t('personal-info')}
            </TabsTrigger>
            <TabsTrigger value="history">
              <FileText className="h-4 w-4 mr-2" />
              {t('medical-history')}
            </TabsTrigger>
            <TabsTrigger value="allergies">
              <AlertCircle className="h-4 w-4 mr-2" />
              {t('allergies')}
            </TabsTrigger>
            <TabsTrigger value="conditions">
              <Heart className="h-4 w-4 mr-2" />
              {t('chronic-conditions')}
            </TabsTrigger>
            <TabsTrigger value="documents">
              <FileText className="h-4 w-4 mr-2" />
              {t('documents')}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="personal">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>{t('personal-info')}</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">{t('first-name')}</p>
                  <p className="font-medium">{patient.first_name_en}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{t('last-name')}</p>
                  <p className="font-medium">{patient.last_name_en}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{t('date-of-birth')}</p>
                  <p className="font-medium">{patient.date_of_birth}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{t('gender')}</p>
                  <p className="font-medium">
                    {patient.gender === 'M' ? t('male') : t('female')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{t('national-id')}</p>
                  <p className="font-medium">{patient.national_id || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{t('city')}</p>
                  <p className="font-medium">{patient.city || 'N/A'}</p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-sm text-muted-foreground">{t('address')}</p>
                  <p className="font-medium">{patient.address || 'N/A'}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>{t('medical-history')}</CardTitle>
              </CardHeader>
              <CardContent>
                {medicalHistory.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No medical history records
                  </p>
                ) : (
                  <div className="space-y-4">
                    {medicalHistory.map((record, index) => (
                      <motion.div
                        key={record.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-4 border border-border rounded-lg hover:border-primary/50 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-semibold text-lg">{record.diagnosis}</p>
                            <p className="text-sm text-muted-foreground mt-1">
                              {record.treatment}
                            </p>
                            {record.notes && (
                              <p className="text-xs text-muted-foreground mt-2">
                                {record.notes}
                              </p>
                            )}
                          </div>
                          <Badge variant="outline">{record.date}</Badge>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="allergies">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>{t('allergies')}</CardTitle>
              </CardHeader>
              <CardContent>
                {allergies.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No allergies recorded
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {allergies.map((allergy, index) => (
                      <motion.div
                        key={allergy.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <Badge variant="destructive" className="text-sm px-3 py-1">
                          {allergy.allergen}
                        </Badge>
                      </motion.div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="conditions">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>{t('chronic-conditions')}</CardTitle>
              </CardHeader>
              <CardContent>
                {chronicConditions.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No chronic conditions recorded
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {chronicConditions.map((condition, index) => (
                      <motion.div
                        key={condition.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <Badge variant="secondary" className="text-sm px-3 py-1">
                          {condition.condition_name}
                        </Badge>
                      </motion.div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documents">
            <Card className="shadow-soft">
              <CardHeader>
                <CardTitle>{t('documents')}</CardTitle>
              </CardHeader>
              <CardContent>
                {documents.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No documents uploaded
                  </p>
                ) : (
                  <div className="space-y-3">
                    {documents.map((doc, index) => (
                      <motion.div
                        key={doc.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between p-3 border border-border rounded-lg hover:border-primary/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{doc.document_type}</p>
                            <p className="text-xs text-muted-foreground">
                              {doc.upload_date}
                            </p>
                          </div>
                        </div>
                        <Badge variant={doc.is_verified ? 'default' : 'secondary'}>
                          {doc.is_verified ? t('verified') : 'Pending'}
                        </Badge>
                      </motion.div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  );
}
