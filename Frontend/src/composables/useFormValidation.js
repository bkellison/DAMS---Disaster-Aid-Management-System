import { reactive, ref, computed } from 'vue';

export default function useFormValidation(initialValues = {}, validationRules = {}) {
  // Form values
  const formValues = reactive({ ...initialValues });
  
  // Form errors
  const errors = reactive({});
  
  // Validation status
  const isValid = ref(true);
  const isDirty = ref(false);
  
  // Validate a single field
  const validateField = (fieldName) => {
    const rules = validationRules[fieldName];
    if (!rules) return true;
    
    let isFieldValid = true;
    const fieldErrors = [];
    
    for (const rule of rules) {
      const result = rule(formValues[fieldName], formValues);
      if (result !== true) {
        isFieldValid = false;
        fieldErrors.push(result);
      }
    }
    
    errors[fieldName] = fieldErrors.length ? fieldErrors[0] : null;
    return isFieldValid;
  };
  
  // Validate all fields
  const validate = () => {
    let valid = true;
    
    for (const fieldName in validationRules) {
      const fieldValid = validateField(fieldName);
      valid = valid && fieldValid;
    }
    
    isValid.value = valid;
    return valid;
  };
  
  // Reset form to initial values
  const reset = () => {
    for (const key in initialValues) {
      formValues[key] = initialValues[key];
    }
    
    for (const key in errors) {
      errors[key] = null;
    }
    
    isValid.value = true;
    isDirty.value = false;
  };
  
  // Handle field changes
  const handleChange = (fieldName, value) => {
    formValues[fieldName] = value;
    isDirty.value = true;
    validateField(fieldName);
  };
  
  // Handle form submission
  const handleSubmit = (submitFn) => {
    return async (event) => {
      event?.preventDefault();
      
      if (validate()) {
        await submitFn(formValues);
      }
    };
  };
  
  return {
    formValues,
    errors,
    isValid,
    isDirty,
    validate,
    validateField,
    reset,
    handleChange,
    handleSubmit
  };
}