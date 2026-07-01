"""
Manage user upload cache, manifest, and cleanup
"""

import json
import os
import pickle
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class CacheManager:
    """Manage user upload cache, manifest, and cleanup"""

    UPLOAD_DIR = ".cache/user_uploads"
    MANIFEST_PATH = ".cache/upload_manifest.json"

    @staticmethod
    def ensure_directories():
        """Create cache directories if they don't exist"""
        Path(".cache").mkdir(exist_ok=True)
        Path(CacheManager.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_upload(df, filename: str):
        """Save DataFrame and profiles, create manifest entry

        Returns: (upload_id, profiles dict)
        """
        from core.data_profiler import DataProfiler

        CacheManager.ensure_directories()

        # Generate upload ID from timestamp
        import secrets
        upload_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(4)


        # Profile the data
        profiler = DataProfiler()
        profiles = profiler.profile(df)

        # Save DataFrame pickle (for performance, consistent with existing codebase)
        df_path = os.path.join(CacheManager.UPLOAD_DIR, f"{upload_id}.pkl")
        with open(df_path, 'wb') as f:
            pickle.dump(df, f)

        # Save profiles JSON
        profiles_path = os.path.join(CacheManager.UPLOAD_DIR, f"{upload_id}-profiles.json")
        profiles_dict = {
            name: {
                'dtype': p.dtype,
                'cardinality': p.cardinality,
                'missing_pct': p.missing_pct,
                'is_temporal': p.is_temporal,
            }
            for name, p in profiles.items()
        }
        with open(profiles_path, 'w') as f:
            json.dump(profiles_dict, f, indent=2, default=str)
            
            
        #  Update manifest safely
            manifest = CacheManager.load_manifest()

            #  Ensure structure exists
            if 'uploads' not in manifest:
                manifest['uploads'] = []

            #  Set active upload
            manifest['active_upload_id'] = upload_id

            #  Remove duplicate entry if exists
            manifest['uploads'] = [
                u for u in manifest.get('uploads', [])
                if u.get('id') != upload_id
            ]

            #  Add new upload entry
            manifest['uploads'].append({
                'id': upload_id,
                'filename': filename,
                'uploaded_at': datetime.now().isoformat(),
                'rows': len(df),
                'cols': len(df.columns),
                'pickle_path': df_path,
                'profiles_path': profiles_path
            })

            #  Save manifest safely
            CacheManager.save_manifest(manifest)

            return upload_id, profiles

        # # Update manifest
        # manifest = CacheManager.load_manifest()
        # manifest['active_upload_id'] = upload_id
        # manifest['uploads'].append({
        #     'id': upload_id,
        #     'filename': filename,
        #     'uploaded_at': datetime.now().isoformat(),
        #     'rows': len(df),
        #     'cols': len(df.columns),
        #     'pickle_path': df_path,
        #     'profiles_path': profiles_path
        # })
        # CacheManager.save_manifest(manifest)

        # return upload_id, profiles

    @staticmethod
    def load_manifest() -> Dict:
        """Load manifest, create if not exists"""
        try:
            with open(CacheManager.MANIFEST_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Manifest load failed: {e}")
            return {'active_upload_id': None, 'uploads': []}

    @staticmethod
    def save_manifest(manifest: Dict):
        """Save manifest to file safely"""
        try:
            # ✅ Ensure directory exists
            Path(".cache").mkdir(exist_ok=True)
            with open(CacheManager.MANIFEST_PATH, 'w') as f:
                json.dump(manifest, f, indent=2, default=str)
        except Exception as e:
            print(f"[ERROR] Failed to save manifest: {e}")

    @staticmethod
    def get_active_upload_path() -> Optional[str]:
        """Get path to active upload pickle"""
        manifest = CacheManager.load_manifest()
        if manifest.get('active_upload_id'):
            active_id = manifest['active_upload_id']
            return os.path.join(CacheManager.UPLOAD_DIR, f"{active_id}.pkl")
        return None

    @staticmethod
    def get_active_upload_profiles_path() -> Optional[str]:
        """Get path to active upload profiles JSON"""
        manifest = CacheManager.load_manifest()
        if manifest.get('active_upload_id'):
            active_id = manifest['active_upload_id']
            return os.path.join(CacheManager.UPLOAD_DIR, f"{active_id}-profiles.json")
        return None

    @staticmethod
    def cleanup_old_uploads(days=7):
        """Delete uploads older than N days"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        manifest = CacheManager.load_manifest()

        remaining = []
        for upload in manifest.get('uploads', []):
            upload_time = datetime.fromisoformat(upload['uploaded_at'])
            if upload_time > cutoff:
                remaining.append(upload)
            else:
                # Delete old files
                try:
                    if os.path.exists(upload['pickle_path']):
                        os.remove(upload['pickle_path'])
                except Exception as e:
                    print(f"[WARN] Failed to delete old upload: {e}")


        manifest['uploads'] = remaining
        CacheManager.save_manifest(manifest)
