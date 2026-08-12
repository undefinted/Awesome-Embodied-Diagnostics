# Maintenance and synchronization

## Canonical workflow

- GitHub private repository: shared canonical history.
- `D:\Researching\清华\古月\Project\综述\code maintainance\awesome-embodied-diagnostics`: primary local working copy.
- `E:\Projects\Review\awesome-embodied-diagnostics`: secondary local clone.

Do not edit the same branch concurrently in both copies. Commit and push from one copy, then run `git pull --ff-only` in the other.

```powershell
git status
git add -A
git commit -m "literature: add verified records"
git push

# In the other working copy
git pull --ff-only
```

`local_only/` is deliberately untracked. It must be backed up or synchronized separately and must not be pushed without a rights review.
