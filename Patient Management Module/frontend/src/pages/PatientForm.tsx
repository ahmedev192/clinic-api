import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import apiService from '@/services/api';
import { toast } from 'sonner';

export default function PatientForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    first_name_en: '',
    last_name_en: '',
    first_name_ar: '',
    last_name_ar: '',
    phone_primary: '',
    email: '',
    date_of_birth: '',
    gender: 'M',
    national_id: '',
    blood_type: '',
    city: '',
    address: '',
    is_active: true,
  });

  useEffect(() => {
    if (id) {
      loadPatient();
    }
  }, [id]);

  const loadPatient = async () => {
    try {
      const data = await apiService.getPatient(id!);
      setFormData({
        first_name_en: data.first_name_en || '',
        last_name_en: data.last_name_en || '',
        first_name_ar: data.first_name_ar || '',
        last_name_ar: data.last_name_ar || '',
        phone_primary: data.phone_primary || '',
        email: data.email || '',
        date_of_birth: data.date_of_birth || '',
        gender: data.gender || 'M',
        national_id: data.national_id || '',
        blood_type: data.blood_type || '',
        city: data.city || '',
        address: data.address || '',
        is_active: data.is_active ?? true,
      });
    } catch (error) {
      toast.error(t('error-occurred'));
      console.error('Failed to load patient:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (id) {
        await apiService.updatePatient(id, formData);
        toast.success('Patient updated successfully');
      } else {
        await apiService.createPatient(formData);
        toast.success('Patient created successfully');
      }
      navigate('/patients');
    } catch (error: any) {
      toast.error(error.response?.data?.message || t('error-occurred'));
      console.error('Failed to save patient:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <Button variant="ghost" size="icon" onClick={() => navigate('/patients')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {id ? t('edit') : t('add-patient')}
          </h1>
          <p className="text-muted-foreground">{t('patient-information')}</p>
        </div>
      </motion.div>

      {/* Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <form onSubmit={handleSubmit}>
          <Card className="shadow-soft">
            <CardHeader>
              <CardTitle>{t('patient-information')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Names */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name_en">{t('first-name')} (EN) *</Label>
                  <Input
                    id="first_name_en"
                    required
                    value={formData.first_name_en}
                    onChange={(e) => handleChange('first_name_en', e.target.value)}
                    placeholder="John"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name_en">{t('last-name')} (EN) *</Label>
                  <Input
                    id="last_name_en"
                    required
                    value={formData.last_name_en}
                    onChange={(e) => handleChange('last_name_en', e.target.value)}
                    placeholder="Doe"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="first_name_ar">{t('first-name')} (AR)</Label>
                  <Input
                    id="first_name_ar"
                    value={formData.first_name_ar}
                    onChange={(e) => handleChange('first_name_ar', e.target.value)}
                    placeholder="جون"
                    dir="rtl"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name_ar">{t('last-name')} (AR)</Label>
                  <Input
                    id="last_name_ar"
                    value={formData.last_name_ar}
                    onChange={(e) => handleChange('last_name_ar', e.target.value)}
                    placeholder="دو"
                    dir="rtl"
                  />
                </div>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone_primary">{t('phone')} *</Label>
                  <Input
                    id="phone_primary"
                    type="tel"
                    required
                    value={formData.phone_primary}
                    onChange={(e) => handleChange('phone_primary', e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">{t('email')}</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    placeholder="patient@email.com"
                  />
                </div>
              </div>

              {/* Personal Info */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date_of_birth">{t('date-of-birth')} *</Label>
                  <Input
                    id="date_of_birth"
                    type="date"
                    required
                    value={formData.date_of_birth}
                    onChange={(e) => handleChange('date_of_birth', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gender">{t('gender')} *</Label>
                  <Select
                    value={formData.gender}
                    onValueChange={(value) => handleChange('gender', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-popover z-50">
                      <SelectItem value="M">{t('male')}</SelectItem>
                      <SelectItem value="F">{t('female')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="blood_type">{t('blood-type')}</Label>
                  <Select
                    value={formData.blood_type}
                    onValueChange={(value) => handleChange('blood_type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('select-option')} />
                    </SelectTrigger>
                    <SelectContent className="bg-popover z-50">
                      <SelectItem value="A+">A+</SelectItem>
                      <SelectItem value="A-">A-</SelectItem>
                      <SelectItem value="B+">B+</SelectItem>
                      <SelectItem value="B-">B-</SelectItem>
                      <SelectItem value="AB+">AB+</SelectItem>
                      <SelectItem value="AB-">AB-</SelectItem>
                      <SelectItem value="O+">O+</SelectItem>
                      <SelectItem value="O-">O-</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Additional Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="national_id">{t('national-id')}</Label>
                  <Input
                    id="national_id"
                    value={formData.national_id}
                    onChange={(e) => handleChange('national_id', e.target.value)}
                    placeholder="1234567890"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="city">{t('city')}</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => handleChange('city', e.target.value)}
                    placeholder="New York"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="address">{t('address')}</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => handleChange('address', e.target.value)}
                  placeholder="123 Main Street"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={loading}
                  className="bg-gradient-primary hover:shadow-glow transition-all"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? t('loading') : t('save')}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/patients')}
                >
                  {t('cancel')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </motion.div>
    </div>
  );
}
