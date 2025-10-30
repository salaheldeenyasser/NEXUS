// App.js
import './App.css';
import { RouterProvider, createBrowserRouter, createRoutesFromElements, Route } from 'react-router-dom';
import Loader from './components/loader';
import CamView from './components/camView';
import Root from './components/root';
import Settings from './components/settings';
import FingerprintPage from './components/FingerprintPage';
import ProfileChoiceMenu from './components/profileChoiceMenu';
import SystemSettings from './components/systemSettings';
import AddProfileNameRole from './components/AddProfileNameRole';
import AddFingerprint from './components/addFingerprint';
import AddFace from './components/addFace';
import ProfileAdded from './components/profileAdded';
import CreateAdmin from './components/createAdmin';
import SelectProfile from './components/selectProfile';
import ChangePINPage from './components/changePin';
import EditProfile from './components/editProfile';
import ChangeRole from './components/changeRole';
import DeleteProfileConfirm from './components/deleteProfileConfirm';
import AdminPinPrompt from './components/AdminPinPrompt';
import ChangeAdminPINPage from './components/changeAdminPin';
import ResetSystem from './components/resetSystem';


function App() {
  const dlRouter = createBrowserRouter(
    createRoutesFromElements(
      <Route path='/' element={<Root />}>
        <Route index element={<Loader />} />
        <Route path='/create-admin' element={<CreateAdmin />} />
        <Route path='/admin-pin-prompt' element={<AdminPinPrompt />} />
        <Route path='/cam-view' element={<CamView />} />
        <Route path='/settings' element={<Settings />} />
        <Route path='/settings/fingerprint-page' element={<FingerprintPage />} />
        <Route path='/settings/profile-choice-menu' element={<ProfileChoiceMenu />} />
        <Route path='/settings/profile-choice-menu/add-profile' element={<AddProfileNameRole />} />
        <Route path='/settings/profile-choice-menu/add-profile/fingerprint' element={<AddFingerprint />} />
        <Route path='/settings/profile-choice-menu/add-profile/face' element={<AddFace />} />
        <Route path='/settings/profile-choice-menu/add-profile/profile-added' element={<ProfileAdded />} />
        <Route path='/settings/profile-choice-menu/manage-profiles' element={<SelectProfile />} />
        <Route path='/settings/profile-choice-menu/manage-profiles/edit-profile/:id' element={<EditProfile />} />
        <Route path='/settings/profile-choice-menu/manage-profiles/:id/change-role' element={<ChangeRole />} />
        <Route path='/settings/profile-choice-menu/manage-profiles/:id/confirm-delete' element={<DeleteProfileConfirm />} />
        <Route path='/settings/change-pin' element={<ChangePINPage />} />
        <Route path="/settings/profile-choice-menu/manage-profiles/:id/change-admin-pin" element={<ChangeAdminPINPage />} />
        <Route path='/settings/system-settings' element={<SystemSettings />} />
        <Route path='/settings/system-settings/reset-system' element={<ResetSystem />} />
      </Route>
    )
  );

  return (
    <div className="app-container">
      <RouterProvider router={dlRouter} />
    </div>
  );
}

export default App;
