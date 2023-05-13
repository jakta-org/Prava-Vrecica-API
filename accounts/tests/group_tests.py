from typing import Any
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import Token, Group, UserGroup, User, EntranceKey
import json

    
class CreateGroupTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            is_active=True,
            is_staff=True,
        )
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

        # create group

        self.group = Group.objects.create(
            type='testgroup',
            meta_data={'key': 'value'}
        )
        self.group.save()

    # TEST GROUP CREATION

    def test_post_group(self):
        url = reverse('create_group')
        data = {
            'type': 'testgroup2'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2)
        self.assertEqual(Group.objects.get(type='testgroup2').type, 'testgroup2')
        self.assertEqual(Group.objects.get(type='testgroup2').id, 2)
        # test user is moderator
        self.assertEqual(UserGroup.objects.count(), 1)
        self.assertEqual(UserGroup.objects.get(user=self.user).is_moderator, True)

    def test_post_group_non_admin(self):
        self.user.is_staff = False
        self.user.save()
        url = reverse('create_group')
        data = {
            'type': 'testgroup2'
        }
        # non admin can create group
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2)
        self.assertEqual(Group.objects.get(type='testgroup2').type, 'testgroup2')
        self.assertEqual(Group.objects.get(type='testgroup2').id, 2)
        # test user is moderator
        self.assertEqual(UserGroup.objects.count(), 1)
        self.assertEqual(UserGroup.objects.get(user=self.user).is_moderator, True)

    def test_post_group_invalid_data(self):
        url = reverse('create_group')
        data = {
            'settings': 'test'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(UserGroup.objects.count(), 0)
    
    def test_post_group_missing_data(self):
        url = reverse('create_group')
        data = {}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(UserGroup.objects.count(), 0)



class GetPutDeleteGroupTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            is_active=True,
            is_staff=True,
        )
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

        # create group

        self.group = Group.objects.create(
            type='testgroup',
            meta_data={'key': 'value'}
        )
        self.group.save()

        self.userGroup = UserGroup.objects.create(user=self.user, group=self.group, is_moderator=True)
        self.userGroup.save()
    
    def test_get_group(self):
        url = reverse('group', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'testgroup')
        self.assertEqual(response.data['meta_data'], {'key': 'value'})

    def test_get_group_invalid_id(self):
        url = reverse('group', args=[123])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_group_user_not_member(self):
        self.userGroup.delete()

        url = reverse('group', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_group_user_not_moderator(self):
        self.userGroup.is_moderator = False
        self.userGroup.save()

        url = reverse('group', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'testgroup')
        self.assertEqual(response.data['meta_data'], {'key': 'value'})

    def test_put_group(self):
        url = reverse('group', args=[self.group.id])
        data = {
            'type': 'testgroup2',
            'meta_data': json.dumps({'key2': 'value2'})
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Group.objects.get(type='testgroup2').type, 'testgroup2')
        self.assertEqual(Group.objects.get(type='testgroup2').meta_data, {'key2': 'value2'})

    def test_put_group_invalid_id(self):
        url = reverse('group', args=[123])
        data = {
            'type': 'testgroup2',
            'meta_data': json.dumps({'key2': 'value2'})
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Group.objects.get(type='testgroup').type, 'testgroup')
        self.assertEqual(Group.objects.get(type='testgroup').meta_data, {'key': 'value'})

    def test_put_group_user_no_change(self):
        url = reverse('group', args=[self.group.id])
        data = {
            'type': 'testgroup',
            'meta_data': json.dumps({'key': 'value'})
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Group.objects.get(type='testgroup').type, 'testgroup')
        self.assertEqual(Group.objects.get(type='testgroup').meta_data, {'key': 'value'})

    def test_put_group_user_extra_data(self):
        url = reverse('group', args=[self.group.id])
        data = {
            'type': 'testgroup',
            'meta_data': json.dumps({'key': 'value', 'key2': 'value2'}),
            'settings': json.dumps({'key': 'value'}),
            'extra': 'extra'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.put(url, data)
        # extra data is ignored
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Group.objects.get(type='testgroup').type, 'testgroup')
        self.assertEqual(Group.objects.get(type='testgroup').meta_data, {'key': 'value', 'key2': 'value2'})
        self.assertEqual(Group.objects.get(type='testgroup').settings, {'key': 'value'})

    def test_delete_group(self):
        url = reverse('group', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Group.objects.filter(is_active=True).count(), 0)
        self.assertEqual(UserGroup.objects.count(), 1)

    def test_delete_group_invalid_id(self):
        url = reverse('group', args=[123])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(UserGroup.objects.count(), 1)

    def test_delete_group_user_not_member(self):
        self.userGroup.delete()

        url = reverse('group', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(UserGroup.objects.count(), 0)

    def test_delete_group_user_not_moderator(self):
        self.userGroup.is_moderator = False
        self.userGroup.save()

        url = reverse('group', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(UserGroup.objects.count(), 1)

class EntranceKeyTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            is_active=True,
            is_staff=True,
        )
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

        # create group

        self.group = Group.objects.create(
            type='testgroup',
            meta_data={'key': 'value'}
        )
        self.group.save()

        self.userGroup = UserGroup.objects.create(user=self.user, group=self.group, is_moderator=True).save()

        self.key = EntranceKey.objects.create(
            group_id=self.group.id,
            uses_left=5,
        )
        self.key.save()

    def test_create_user_with_key(self):
        url = reverse('create_user')
        data = {
            'email': 'test2@example.com',
            'username': 'testuser2',
            'password': 'testpassword',
            'entrance_code': self.key.code
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

        # test user is in group
        self.assertEqual(UserGroup.objects.count(), 2)
        self.assertEqual(UserGroup.objects.get(
            user=User.objects.get(username='testuser2')).group_id, 1)
        
        # test key uses_left
        self.assertEqual(EntranceKey.objects.get(code=self.key.code).uses_left, 4)

class GroupTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            is_active=True,
            is_staff=True,
        )
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

        self.user2 = User.objects.create_user(
            email='test2@example.com',
            username='testuser2',
            password='testpassword',
            is_active=True,
            is_staff=False,
        )
        self.user2.save()
        self.token2 = Token.objects.create(user=self.user2)
        self.token2.save()


        # create group

        self.group = Group.objects.create(
            type='testgroup',
            meta_data={'key': 'value'}
        )
        self.group.save()

        self.userGroup = UserGroup.objects.create(user=self.user, group=self.group, is_moderator=True)
        self.userGroup.save()

    def test_user_groups(self):
        url = reverse('user_groups', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_groups_invalid_id(self):
        url = reverse('user_groups', args=[123])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_groups_user_not_member(self):
        self.userGroup.delete()

        url = reverse('user_groups', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        # user is not member of any group
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_groups_user_not_moderator(self):
        self.userGroup.is_moderator = False
        self.userGroup.save()

        url = reverse('user_groups', args=[self.user.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # TEST GROUP MEMBERS

    def test_group_members(self):
        UserGroup.objects.create(user=self.user2, group=self.group, is_moderator=False).save()

        url = reverse('group_members', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn('group_score', response.data[0])
        self.assertIn('group_score', response.data[1])
        self.assertIn('user', response.data[0])
        self.assertIn('user', response.data[1])

        self.assertEqual(response.data[0]['user']['username'], 'testuser')

    def test_group_members_invalid_id(self):
        url = reverse('group_members', args=[123])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_group_members_user_not_member(self):
        self.userGroup.delete()

        url = reverse('group_members', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_members_user_not_moderator(self):
        self.userGroup.is_moderator = False
        self.userGroup.save()

        url = reverse('group_members', args=[self.group.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

