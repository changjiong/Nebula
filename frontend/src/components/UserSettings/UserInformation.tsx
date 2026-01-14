import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Camera, Loader2, Trash2 } from "lucide-react"
import { useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { UsersService, type UserUpdateMe } from "@/client"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { getInitials, handleError } from "@/utils"

const formSchema = z.object({
  full_name: z.string().max(30).optional(),
  email: z.email({ message: "Invalid email address" }),
})

type FormData = z.infer<typeof formSchema>

const UserInformation = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [editMode, setEditMode] = useState(false)
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false)
  const { user: currentUser } = useAuth()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      full_name: currentUser?.full_name ?? undefined,
      email: currentUser?.email,
    },
  })

  const toggleEditMode = () => {
    setEditMode(!editMode)
  }

  const mutation = useMutation({
    mutationFn: (data: UserUpdateMe) =>
      UsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("User updated successfully")
      toggleEditMode()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries()
    },
  })

  const onSubmit = (data: FormData) => {
    const updateData: UserUpdateMe = {}

    // only include fields that have changed
    if (data.full_name !== currentUser?.full_name) {
      updateData.full_name = data.full_name
    }
    if (data.email !== currentUser?.email) {
      updateData.email = data.email
    }

    mutation.mutate(updateData)
  }

  const onCancel = () => {
    form.reset()
    toggleEditMode()
  }

  const handleAvatarClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if (!allowedTypes.includes(file.type)) {
      showErrorToast(
        "Invalid file type. Please upload JPEG, PNG, WebP, or GIF.",
      )
      return
    }

    // Validate file size (2MB max)
    if (file.size > 2 * 1024 * 1024) {
      showErrorToast("File too large. Maximum size is 2MB.")
      return
    }

    setIsUploadingAvatar(true)
    try {
      const formData = new FormData()
      formData.append("file", file)

      const token = localStorage.getItem("access_token")
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/users/me/avatar`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Upload failed")
      }

      showSuccessToast("Avatar uploaded successfully")
      queryClient.invalidateQueries()
    } catch (error) {
      showErrorToast(error instanceof Error ? error.message : "Upload failed")
    } finally {
      setIsUploadingAvatar(false)
      // Reset the input
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  const handleDeleteAvatar = async () => {
    setIsUploadingAvatar(true)
    try {
      const token = localStorage.getItem("access_token")
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/users/me/avatar`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Delete failed")
      }

      showSuccessToast("Avatar removed")
      queryClient.invalidateQueries()
    } catch (error) {
      showErrorToast(error instanceof Error ? error.message : "Delete failed")
    } finally {
      setIsUploadingAvatar(false)
    }
  }

  return (
    <div className="max-w-md">
      <h3 className="text-lg font-semibold py-4">User Information</h3>

      {/* Avatar Section */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative group">
          <Avatar
            className="size-20 cursor-pointer"
            onClick={handleAvatarClick}
          >
            <AvatarImage
              src={
                currentUser?.avatar_url
                  ? `${import.meta.env.VITE_API_URL}${currentUser.avatar_url}`
                  : undefined
              }
              alt={currentUser?.full_name || "User"}
            />
            <AvatarFallback className="bg-zinc-600 text-white text-xl">
              {getInitials(currentUser?.full_name || "User")}
            </AvatarFallback>
          </Avatar>

          {/* Overlay for upload */}
          <div
            className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
            onClick={handleAvatarClick}
          >
            {isUploadingAvatar ? (
              <Loader2 className="size-6 text-white animate-spin" />
            ) : (
              <Camera className="size-6 text-white" />
            )}
          </div>

          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            className="hidden"
            onChange={handleFileChange}
            disabled={isUploadingAvatar}
          />
        </div>

        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium">Profile Photo</p>
          <p className="text-xs text-muted-foreground">
            Click to upload (max 2MB)
          </p>
          {currentUser?.avatar_url && (
            <Button
              variant="ghost"
              size="sm"
              className="text-destructive hover:text-destructive h-7 px-2"
              onClick={handleDeleteAvatar}
              disabled={isUploadingAvatar}
            >
              <Trash2 className="size-3 mr-1" />
              Remove
            </Button>
          )}
        </div>
      </div>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-4"
        >
          <FormField
            control={form.control}
            name="full_name"
            render={({ field }) =>
              editMode ? (
                <FormItem>
                  <FormLabel>Full name</FormLabel>
                  <FormControl>
                    <Input type="text" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              ) : (
                <FormItem>
                  <FormLabel>Full name</FormLabel>
                  <p
                    className={cn(
                      "py-2 truncate max-w-sm",
                      !field.value && "text-muted-foreground",
                    )}
                  >
                    {field.value || "N/A"}
                  </p>
                </FormItem>
              )
            }
          />

          <FormField
            control={form.control}
            name="email"
            render={({ field }) =>
              editMode ? (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input type="email" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              ) : (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <p className="py-2 truncate max-w-sm">{field.value}</p>
                </FormItem>
              )
            }
          />

          <div className="flex gap-3">
            {editMode ? (
              <>
                <LoadingButton
                  type="submit"
                  loading={mutation.isPending}
                  disabled={!form.formState.isDirty}
                >
                  Save
                </LoadingButton>
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                  disabled={mutation.isPending}
                >
                  Cancel
                </Button>
              </>
            ) : (
              <Button type="button" onClick={toggleEditMode}>
                Edit
              </Button>
            )}
          </div>
        </form>
      </Form>
    </div>
  )
}

export default UserInformation
