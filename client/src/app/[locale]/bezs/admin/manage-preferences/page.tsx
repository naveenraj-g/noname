import { PreferenceTemplateListTable } from "@/modules/client/admin/components/tables/preference-template-list-table/preference-template-list-table";
import { getAllPreferenceTemplates } from "@/modules/client/admin/server-actions/preferenceTemplate-actions";

const ManagePreferences = async () => {
  const [data, error] = await getAllPreferenceTemplates();

  return (
    <div>
      <PreferenceTemplateListTable
        preferenceTemplateDatas={data}
        error={error}
      />
    </div>
  );
};

export default ManagePreferences;
